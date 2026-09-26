#!/usr/bin/env python3

import random
import shutil
import zipfile
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

KEEP_DAYS = 0.05
BATCH_SIZE = 50
ALL_SEPARATE_FILES = True
RELEASE_KEEP = 5


def weighted_versions(latest: int, supported: int):
    versions = []
    for v in range(supported, latest + 1):
        d = latest - v
        w = 40 if d == 0 else 25 if d == 1 else 15 if d == 2 else 8 if d == 3 else 3 if d <= 6 else 1
        versions.append((v, w))
    return versions


BROWSERS = {
    "Chrome":               {"engine": "Blink",    "popularity": 65, "versions": weighted_versions(131, 100)},
    "Chrome-Beta":          {"engine": "Blink",    "popularity": 1,  "versions": [(132, 1)]},
    "Chrome-Canary":        {"engine": "Blink",    "popularity": 1,  "versions": [(133, 1)]},
    "Chrome-Dev":           {"engine": "Blink",    "popularity": 1,  "versions": [(132, 1)]},
    "Chrome-Headless":      {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(131, 100)},
    "Chromium":             {"engine": "Blink",    "popularity": 2,  "versions": weighted_versions(131, 100)},
    "Chromium-Beta":        {"engine": "Blink",    "popularity": 1,  "versions": [(132, 1)]},
    "Ungoogled-Chromium":   {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(131, 100)},
    "Brave":                {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(131, 100)},
    "Brave-Beta":           {"engine": "Blink",    "popularity": 1,  "versions": [(132, 1)]},
    "Brave-Nightly":        {"engine": "Blink",    "popularity": 1,  "versions": [(133, 1)]},
    "Edge":                 {"engine": "Blink",    "popularity": 5,  "versions": weighted_versions(131, 100)},
    "Edge-Beta":            {"engine": "Blink",    "popularity": 1,  "versions": [(132, 1)]},
    "Edge-Dev":             {"engine": "Blink",    "popularity": 1,  "versions": [(132, 1)]},
    "Edge-Canary":          {"engine": "Blink",    "popularity": 1,  "versions": [(133, 1)]},
    "Opera":                {"engine": "Blink",    "popularity": 2,  "versions": weighted_versions(116, 95)},
    "Opera-GX":             {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(116, 95)},
    "Opera-Air":            {"engine": "Blink",    "popularity": 1,  "versions": [(4, 1), (3, 1)]},
    "Opera-Beta":           {"engine": "Blink",    "popularity": 1,  "versions": [(117, 1)]},
    "Opera-Developer":      {"engine": "Blink",    "popularity": 1,  "versions": [(117, 1)]},
    "Vivaldi":              {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(7, 4)},
    "Vivaldi-Snapshot":     {"engine": "Blink",    "popularity": 1,  "versions": [(8, 1)]},
    "Yandex":               {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(25, 20)},
    "Yandex-Beta":          {"engine": "Blink",    "popularity": 1,  "versions": [(26, 1)]},
    "Samsung-Internet":     {"engine": "Blink",    "popularity": 2,  "versions": weighted_versions(26, 18)},
    "Samsung-Internet-Beta":{"engine": "Blink",    "popularity": 1,  "versions": [(27, 1)]},
    "UC-Browser":           {"engine": "Blink",    "popularity": 1,  "versions": [(13, 3), (12, 1)]},
    "UC-Browser-Mini":      {"engine": "WebKit",   "popularity": 1,  "versions": [(13, 1)]},
    "DuckDuckGo":           {"engine": "Blink",    "popularity": 1,  "versions": [(7, 2), (6, 1)]},
    "Epic":                 {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(120, 100)},
    "Avast-Secure":         {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(125, 100)},
    "AVG-Secure":           {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(125, 100)},
    "Comodo-Dragon":        {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(130, 100)},
    "Torch":                {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(70, 60)},
    "Slimjet":              {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(40, 35)},
    "Coc-Coc":              {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(120, 100)},
    "360-Browser":          {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(16, 14)},
    "QQ-Browser":           {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(15, 12)},
    "Maxthon":              {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(8, 6)},
    "Puffin":               {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(11, 9)},
    "Ghost-Browser":        {"engine": "Blink",    "popularity": 1,  "versions": [(2, 1)]},
    "Iron":                 {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(130, 100)},
    "Iridium":              {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(130, 100)},
    "Cent-Browser":         {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(6, 4)},
    "Dissenter":            {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(100, 90)},
    "Naver-Whale":          {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(5, 3)},
    "Android-WebView":      {"engine": "Blink",    "popularity": 1,  "versions": weighted_versions(131, 100)},
    "Chrome-Mobile":        {"engine": "Blink",    "popularity": 3,  "versions": weighted_versions(131, 100)},
    "Firefox":              {"engine": "Gecko",    "popularity": 3,  "versions": weighted_versions(134, 110)},
    "Firefox-Beta":         {"engine": "Gecko",    "popularity": 1,  "versions": [(135, 1)]},
    "Firefox-Nightly":      {"engine": "Gecko",    "popularity": 1,  "versions": [(136, 1)]},
    "Firefox-Developer":    {"engine": "Gecko",    "popularity": 1,  "versions": [(134, 1)]},
    "Firefox-ESR":          {"engine": "Gecko",    "popularity": 1,  "versions": [(128, 3), (115, 1)]},
    "Firefox-Focus":        {"engine": "Gecko",    "popularity": 1,  "versions": weighted_versions(130, 120)},
    "Firefox-Mobile":       {"engine": "Gecko",    "popularity": 1,  "versions": weighted_versions(134, 110)},
    "Waterfox":             {"engine": "Gecko",    "popularity": 1,  "versions": weighted_versions(6, 5)},
    "Waterfox-Classic":     {"engine": "Gecko",    "popularity": 1,  "versions": [(56, 1)]},
    "Waterfox-Current":     {"engine": "Gecko",    "popularity": 1,  "versions": weighted_versions(6, 5)},
    "LibreWolf":            {"engine": "Gecko",    "popularity": 1,  "versions": weighted_versions(134, 110)},
    "GNU-IceCat":           {"engine": "Gecko",    "popularity": 1,  "versions": weighted_versions(128, 115)},
    "SeaMonkey":            {"engine": "Gecko",    "popularity": 1,  "versions": [(2, 1)]},
    "Tor-Browser":          {"engine": "Gecko",    "popularity": 1,  "versions": [(14, 3), (13, 2), (12, 1)]},
    "Mullvad-Browser":      {"engine": "Gecko",    "popularity": 1,  "versions": [(14, 2), (13, 1)]},
    "Pale-Moon":            {"engine": "Goanna",   "popularity": 1,  "versions": [(33, 2), (32, 1), (31, 1)]},
    "Basilisk":             {"engine": "Goanna",   "popularity": 1,  "versions": [(2025, 1), (2024, 1)]},
    "Comodo-IceDragon":     {"engine": "Gecko",    "popularity": 1,  "versions": weighted_versions(130, 100)},
    "Safari":               {"engine": "WebKit",   "popularity": 18, "versions": [(18, 40), (17, 35), (16, 15), (15, 7), (14, 3), (13, 1), (12, 1)]},
    "Mobile-Safari":        {"engine": "WebKit",   "popularity": 10, "versions": [(18, 40), (17, 35), (16, 15), (15, 7), (14, 3), (13, 1), (12, 1)]},
    "Safari-TP":            {"engine": "WebKit",   "popularity": 1,  "versions": [(190, 1)]},
    "WebKit-Nightly":       {"engine": "WebKit",   "popularity": 1,  "versions": [(2025, 1), (2024, 1)]},
    "iOS-WebView":          {"engine": "WebKit",   "popularity": 1,  "versions": [(18, 3), (17, 2), (16, 1), (15, 1)]},
    "Epiphany":             {"engine": "WebKit",   "popularity": 1,  "versions": weighted_versions(46, 40)},
    "Midori":               {"engine": "WebKit",   "popularity": 1,  "versions": weighted_versions(11, 9)},
    "Falkon":               {"engine": "WebKit",   "popularity": 1,  "versions": weighted_versions(3, 2)},
    "Konqueror":            {"engine": "KHTML",    "popularity": 1,  "versions": weighted_versions(24, 20)},
    "Electron":             {"engine": "Electron", "popularity": 1,  "versions": weighted_versions(33, 20)},
    "Discord":              {"engine": "Electron", "popularity": 1,  "versions": [(1, 1)]},
    "Slack":                {"engine": "Electron", "popularity": 1,  "versions": [(4, 1)]},
    "Spotify":              {"engine": "Electron", "popularity": 1,  "versions": [(1, 1)]},
    "WhatsApp-Desktop":     {"engine": "Electron", "popularity": 1,  "versions": [(2, 1)]},
    "Telegram-Desktop":     {"engine": "Electron", "popularity": 1,  "versions": [(5, 1), (4, 1)]},
    "Signal-Desktop":       {"engine": "Electron", "popularity": 1,  "versions": [(7, 1), (6, 1)]},
    "Postman":              {"engine": "Electron", "popularity": 1,  "versions": [(11, 2), (10, 1)]},
    "Insomnia":             {"engine": "Electron", "popularity": 1,  "versions": [(2025, 1), (2024, 1)]},
    "Notion":               {"engine": "Electron", "popularity": 1,  "versions": [(3, 1)]},
    "Figma":                {"engine": "Electron", "popularity": 1,  "versions": [(100, 1)]},
    "VSCode":               {"engine": "Electron", "popularity": 1,  "versions": [(1, 1)]},
    "Googlebot":            {"engine": "Custom",   "popularity": 1,  "versions": [(2, 1)]},
    "Googlebot-Image":      {"engine": "Custom",   "popularity": 1,  "versions": [(2, 1)]},
    "Googlebot-News":       {"engine": "Custom",   "popularity": 1,  "versions": [(2, 1)]},
    "Googlebot-Video":      {"engine": "Custom",   "popularity": 1,  "versions": [(2, 1)]},
    "Bingbot":              {"engine": "Custom",   "popularity": 1,  "versions": [(2, 1)]},
    "YandexBot":            {"engine": "Custom",   "popularity": 1,  "versions": [(3, 1)]},
    "DuckDuckBot":          {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "Baiduspider":          {"engine": "Custom",   "popularity": 1,  "versions": [(2, 1)]},
    "Sogou":                {"engine": "Custom",   "popularity": 1,  "versions": [(2, 1)]},
    "Exabot":               {"engine": "Custom",   "popularity": 1,  "versions": [(3, 1)]},
    "Applebot":             {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "facebookexternalhit":  {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "Twitterbot":           {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "LinkedInBot":          {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "Slackbot":             {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "TelegramBot":          {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "Discordbot":           {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "Pinterestbot":         {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "AhrefsBot":            {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "SemrushBot":           {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "MJ12bot":              {"engine": "Custom",   "popularity": 1,  "versions": [(1, 1)]},
    "Curl":                 {"engine": "CLI",      "popularity": 1,  "versions": [(8, 3), (7, 1)]},
    "Wget":                 {"engine": "CLI",      "popularity": 1,  "versions": [(1, 1)]},
    "HTTPie":               {"engine": "CLI",      "popularity": 1,  "versions": [(3, 1)]},
    "Axios":                {"engine": "CLI",      "popularity": 1,  "versions": [(1, 1)]},
    "Python-requests":      {"engine": "CLI",      "popularity": 1,  "versions": [(2, 1)]},
    "Go-http-client":       {"engine": "CLI",      "popularity": 1,  "versions": [(2, 1)]},
    "Java":                 {"engine": "CLI",      "popularity": 1,  "versions": [(21, 1)]},
    "Node-fetch":           {"engine": "CLI",      "popularity": 1,  "versions": [(3, 1)]},
    "OkHttp":               {"engine": "CLI",      "popularity": 1,  "versions": [(5, 1)]},
    "PostmanRuntime":       {"engine": "CLI",      "popularity": 1,  "versions": [(7, 1)]},
    "Google-HTTP-Java":     {"engine": "CLI",      "popularity": 1,  "versions": [(1, 1)]},
    "libwww-perl":          {"engine": "CLI",      "popularity": 1,  "versions": [(6, 1)]},
    "Lynx":                 {"engine": "Text",     "popularity": 1,  "versions": [(2, 2), (2.9, 1)]},
    "w3m":                  {"engine": "Text",     "popularity": 1,  "versions": [(0.5, 1)]},
    "ELinks":               {"engine": "Text",     "popularity": 1,  "versions": [(0.13, 1)]},
    "Links":                {"engine": "Text",     "popularity": 1,  "versions": [(2.29, 1)]},
}


OPERATING_SYSTEMS = {
    "Windows-11":            {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 40},
    "Windows-11-ARM":        {"platform_tpl": "Windows NT 10.0; ARM64",     "family": "Windows", "popularity": 1},
    "Windows-10":            {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 30},
    "Windows-8.1":           {"platform_tpl": "Windows NT 6.3; Win64; x64",  "family": "Windows", "popularity": 1},
    "Windows-8":             {"platform_tpl": "Windows NT 6.2; Win64; x64",  "family": "Windows", "popularity": 1},
    "Windows-7":             {"platform_tpl": "Windows NT 6.1; Win64; x64",  "family": "Windows", "popularity": 1},
    "Windows-Vista":         {"platform_tpl": "Windows NT 6.0; Win64; x64",  "family": "Windows", "popularity": 1},
    "Windows-XP":            {"platform_tpl": "Windows NT 5.1; x86",         "family": "Windows", "popularity": 1},
    "Windows-Server-2025":   {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 1},
    "Windows-Server-2022":   {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 1},
    "Windows-Server-2019":   {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 1},
    "Windows-Server-2016":   {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 1},
    "Windows-Server-2012":   {"platform_tpl": "Windows NT 6.3; Win64; x64",  "family": "Windows", "popularity": 1},
    "Windows-Server-2008":   {"platform_tpl": "Windows NT 6.0; Win64; x64",  "family": "Windows", "popularity": 1},
    "Windows-Phone-10":      {"platform_tpl": "Windows Phone 10.0; Android 4.2.1", "family": "Windows", "popularity": 1},
    "macOS-15-Sequoia":      {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 6},
    "macOS-14-Sonoma":       {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 5},
    "macOS-13-Ventura":      {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 3},
    "macOS-12-Monterey":     {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 2},
    "macOS-11-BigSur":       {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 2},
    "macOS-10.15-Catalina":  {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 1},
    "macOS-10.14-Mojave":    {"platform_tpl": "Macintosh; Intel Mac OS X 10_14_6", "family": "macOS", "popularity": 1},
    "macOS-10.13-HighSierra":{"platform_tpl": "Macintosh; Intel Mac OS X 10_13_6", "family": "macOS", "popularity": 1},
    "macOS-10.12-Sierra":    {"platform_tpl": "Macintosh; Intel Mac OS X 10_12_6", "family": "macOS", "popularity": 1},
    "macOS-10.11-ElCapitan": {"platform_tpl": "Macintosh; Intel Mac OS X 10_11_6", "family": "macOS", "popularity": 1},
    "macOS-10.10-Yosemite":  {"platform_tpl": "Macintosh; Intel Mac OS X 10_10_5", "family": "macOS", "popularity": 1},
    "macOS-ARM-M1":          {"platform_tpl": "Macintosh; ARM Mac OS X 11_0_0",    "family": "macOS", "popularity": 2},
    "macOS-ARM-M2":          {"platform_tpl": "Macintosh; ARM Mac OS X 13_0_0",    "family": "macOS", "popularity": 3},
    "macOS-ARM-M3":          {"platform_tpl": "Macintosh; ARM Mac OS X 14_0_0",    "family": "macOS", "popularity": 3},
    "macOS-ARM-M4":          {"platform_tpl": "Macintosh; ARM Mac OS X 15_0_0",    "family": "macOS", "popularity": 1},
    "Ubuntu-24.04":          {"platform_tpl": "X11; Ubuntu; Linux x86_64", "family": "Linux", "popularity": 2},
    "Ubuntu-23.10":          {"platform_tpl": "X11; Ubuntu; Linux x86_64", "family": "Linux", "popularity": 1},
    "Ubuntu-22.04":          {"platform_tpl": "X11; Ubuntu; Linux x86_64", "family": "Linux", "popularity": 1},
    "Ubuntu-20.04":          {"platform_tpl": "X11; Ubuntu; Linux x86_64", "family": "Linux", "popularity": 1},
    "Ubuntu-18.04":          {"platform_tpl": "X11; Ubuntu; Linux x86_64", "family": "Linux", "popularity": 1},
    "Ubuntu-16.04":          {"platform_tpl": "X11; Ubuntu; Linux x86_64", "family": "Linux", "popularity": 1},
    "Debian-12":             {"platform_tpl": "X11; Linux x86_64", "family": "Linux", "popularity": 1},
    "Debian-11":             {"platform_tpl": "X11; Linux x86_64", "family": "Linux", "popularity": 1},
    "Debian-10":             {"platform_tpl": "X11; Linux x86_64", "family": "Linux", "popularity": 1},
    "Debian-9":              {"platform_tpl": "X11; Linux x86_64", "family": "Linux", "popularity": 1},
    "Fedora-40":             {"platform_tpl": "X11; Fedora; Linux x86_64", "family": "Linux", "popularity": 1},
    "Fedora-39":             {"platform_tpl": "X11; Fedora; Linux x86_64", "family": "Linux", "popularity": 1},
    "Fedora-38":             {"platform_tpl": "X11; Fedora; Linux x86_64", "family": "Linux", "popularity": 1},
    "RHEL-9":                {"platform_tpl": "X11; Red Hat; Linux x86_64", "family": "Linux", "popularity": 1},
    "RHEL-8":                {"platform_tpl": "X11; Red Hat; Linux x86_64", "family": "Linux", "popularity": 1},
    "CentOS-8":              {"platform_tpl": "X11; CentOS; Linux x86_64", "family": "Linux", "popularity": 1},
    "CentOS-7":              {"platform_tpl": "X11; CentOS; Linux x86_64", "family": "Linux", "popularity": 1},
    "AlmaLinux-9":           {"platform_tpl": "X11; AlmaLinux; Linux x86_64", "family": "Linux", "popularity": 1},
    "Rocky-Linux-9":         {"platform_tpl": "X11; Rocky Linux; Linux x86_64", "family": "Linux", "popularity": 1},
    "Arch-Linux":            {"platform_tpl": "X11; Arch Linux; Linux x86_64", "family": "Linux", "popularity": 1},
    "Manjaro":               {"platform_tpl": "X11; Manjaro; Linux x86_64", "family": "Linux", "popularity": 1},
    "EndeavourOS":           {"platform_tpl": "X11; EndeavourOS; Linux x86_64", "family": "Linux", "popularity": 1},
    "Garuda":                {"platform_tpl": "X11; Garuda; Linux x86_64", "family": "Linux", "popularity": 1},
    "Linux-Mint":            {"platform_tpl": "X11; Linux Mint; Linux x86_64", "family": "Linux", "popularity": 1},
    "openSUSE-Leap":         {"platform_tpl": "X11; openSUSE; Linux x86_64", "family": "Linux", "popularity": 1},
    "openSUSE-Tumbleweed":   {"platform_tpl": "X11; openSUSE; Linux x86_64", "family": "Linux", "popularity": 1},
    "Alpine-Linux":          {"platform_tpl": "X11; Alpine Linux; Linux x86_64", "family": "Linux", "popularity": 1},
    "Gentoo":                {"platform_tpl": "X11; Gentoo; Linux x86_64", "family": "Linux", "popularity": 1},
    "Slackware":             {"platform_tpl": "X11; Slackware; Linux x86_64", "family": "Linux", "popularity": 1},
    "Kali-Linux":            {"platform_tpl": "X11; Kali Linux; Linux x86_64", "family": "Linux", "popularity": 1},
    "Parrot-OS":             {"platform_tpl": "X11; Parrot; Linux x86_64", "family": "Linux", "popularity": 1},
    "Tails":                 {"platform_tpl": "X11; Tails; Linux x86_64", "family": "Linux", "popularity": 1},
    "Qubes-OS":              {"platform_tpl": "X11; Qubes; Linux x86_64", "family": "Linux", "popularity": 1},
    "NixOS":                 {"platform_tpl": "X11; NixOS; Linux x86_64", "family": "Linux", "popularity": 1},
    "Pop-OS":                {"platform_tpl": "X11; Pop; Linux x86_64", "family": "Linux", "popularity": 1},
    "Elementary-OS":         {"platform_tpl": "X11; elementary OS; Linux x86_64", "family": "Linux", "popularity": 1},
    "Zorin-OS":              {"platform_tpl": "X11; Zorin OS; Linux x86_64", "family": "Linux", "popularity": 1},
    "Deepin":                {"platform_tpl": "X11; Deepin; Linux x86_64", "family": "Linux", "popularity": 1},
    "MX-Linux":              {"platform_tpl": "X11; MX Linux; Linux x86_64", "family": "Linux", "popularity": 1},
    "Puppy-Linux":           {"platform_tpl": "X11; Puppy; Linux x86_64", "family": "Linux", "popularity": 1},
    "Android-15":            {"platform_tpl": "Linux; Android 15",     "family": "Android", "popularity": 8},
    "Android-14":            {"platform_tpl": "Linux; Android 14",     "family": "Android", "popularity": 10},
    "Android-13":            {"platform_tpl": "Linux; Android 13",     "family": "Android", "popularity": 7},
    "Android-12":            {"platform_tpl": "Linux; Android 12",     "family": "Android", "popularity": 4},
    "Android-11":            {"platform_tpl": "Linux; Android 11",     "family": "Android", "popularity": 3},
    "Android-10":            {"platform_tpl": "Linux; Android 10",     "family": "Android", "popularity": 2},
    "Android-9":             {"platform_tpl": "Linux; Android 9",      "family": "Android", "popularity": 1},
    "Android-8":             {"platform_tpl": "Linux; Android 8.1.0",  "family": "Android", "popularity": 1},
    "Android-7":             {"platform_tpl": "Linux; Android 7.1.2",  "family": "Android", "popularity": 1},
    "Android-6":             {"platform_tpl": "Linux; Android 6.0.1",  "family": "Android", "popularity": 1},
    "iOS-18":                {"platform_tpl": "iPhone; CPU iPhone OS 18_0 like Mac OS X", "family": "iOS", "popularity": 12},
    "iOS-17":                {"platform_tpl": "iPhone; CPU iPhone OS 17_0 like Mac OS X", "family": "iOS", "popularity": 15},
    "iOS-16":                {"platform_tpl": "iPhone; CPU iPhone OS 16_0 like Mac OS X", "family": "iOS", "popularity": 8},
    "iOS-15":                {"platform_tpl": "iPhone; CPU iPhone OS 15_0 like Mac OS X", "family": "iOS", "popularity": 3},
    "iOS-14":                {"platform_tpl": "iPhone; CPU iPhone OS 14_0 like Mac OS X", "family": "iOS", "popularity": 1},
    "iOS-13":                {"platform_tpl": "iPhone; CPU iPhone OS 13_0 like Mac OS X", "family": "iOS", "popularity": 1},
    "iPadOS-18":             {"platform_tpl": "iPad; CPU OS 18_0 like Mac OS X", "family": "iOS", "popularity": 4},
    "iPadOS-17":             {"platform_tpl": "iPad; CPU OS 17_0 like Mac OS X", "family": "iOS", "popularity": 5},
    "iPadOS-16":             {"platform_tpl": "iPad; CPU OS 16_0 like Mac OS X", "family": "iOS", "popularity": 2},
    "FreeBSD-14":            {"platform_tpl": "X11; FreeBSD amd64", "family": "BSD", "popularity": 1},
    "FreeBSD-13":            {"platform_tpl": "X11; FreeBSD amd64", "family": "BSD", "popularity": 1},
    "OpenBSD":               {"platform_tpl": "X11; OpenBSD amd64", "family": "BSD", "popularity": 1},
    "NetBSD":                {"platform_tpl": "X11; NetBSD amd64", "family": "BSD", "popularity": 1},
    "DragonFly-BSD":         {"platform_tpl": "X11; DragonFly amd64", "family": "BSD", "popularity": 1},
    "Chrome-OS":             {"platform_tpl": "X11; CrOS x86_64", "family": "ChromeOS", "popularity": 1},
    "Chrome-OS-ARM":         {"platform_tpl": "X11; CrOS aarch64", "family": "ChromeOS", "popularity": 1},
    "Solaris":               {"platform_tpl": "X11; SunOS sun4u", "family": "Unix", "popularity": 1},
    "AIX":                   {"platform_tpl": "AIX", "family": "Unix", "popularity": 1},
    "Haiku":                 {"platform_tpl": "X11; Haiku x86_64", "family": "Other", "popularity": 1},
    "ReactOS":               {"platform_tpl": "Windows NT 5.2; ReactOS", "family": "Other", "popularity": 1},
    "Fuchsia":               {"platform_tpl": "X11; Fuchsia", "family": "Other", "popularity": 1},
    "HarmonyOS-4":           {"platform_tpl": "Linux; HarmonyOS 4.0", "family": "Other", "popularity": 1},
    "KaiOS-3":               {"platform_tpl": "Mobile; KaiOS 3.0", "family": "Other", "popularity": 1},
    "Sailfish-OS":           {"platform_tpl": "Linux; Sailfish", "family": "Other", "popularity": 1},
    "Tizen-6.5":             {"platform_tpl": "Linux; Tizen 6.5", "family": "Other", "popularity": 1},
    "WebOS-6":               {"platform_tpl": "Linux; webOS 6.0", "family": "Other", "popularity": 1},
}


def pick_version(browser_info):
    versions = [v for v, w in browser_info["versions"]]
    weights  = [w for v, w in browser_info["versions"]]
    return random.choices(versions, weights=weights, k=1)[0]


def build_ua(browser_name, version, os_name, os_info):
    browser_info = BROWSERS[browser_name]
    engine = browser_info["engine"]
    platform = os_info["platform_tpl"]
    b = browser_name.lower()

    if engine in ("Blink", "Electron"):
        chrome_ver = version if b == "chrome" else random.randint(100, 131)
        if "edge" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36 Edg/{chrome_ver}.0.0.0"
        if "opera" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36 OPR/{version}.0.0.0"
        if "vivaldi" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36 Vivaldi/{version}.0"
        if "yandex" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 YaBrowser/{version}.0 Safari/537.36"
        if "samsung" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Mobile Safari/537.36 SamsungBrowser/{version}.0"
        if "uc-browser-mini" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Version/{version}.0 Mobile Safari/537.36"
        if "uc-browser" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Version/{version}.0 UCBrowser/{version}.0.0.0 Mobile Safari/537.36"
        if "duckduckgo" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36 DuckDuckGo/{version}"
        if "brave" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36"
        if "headless" in b:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/{chrome_ver}.0.0.0 Safari/537.36"
        if engine == "Electron":
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) {browser_name}/{version}.0.0 Chrome/{chrome_ver}.0.0.0 Electron/{version}.0.0 Safari/537.36"
        return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.{random.randint(1000,9999)}.{random.randint(50,200)} Safari/537.36"

    if engine == "Gecko":
        return f"Mozilla/5.0 ({platform}; rv:{version}.0) Gecko/20100101 Firefox/{version}.0"

    if engine == "Goanna":
        return f"Mozilla/5.0 ({platform}; rv:{version}.0) Gecko/20100101 {browser_name}/{version}.0"

    if engine == "WebKit":
        if "mobile" in b or os_info["family"] == "iOS":
            ios_ver = version if version < 100 else random.randint(12, 18)
            return f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_ver}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ios_ver}.0 Mobile/15E148 Safari/604.1"
        return f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version}.0 Safari/605.1.15"

    if engine == "KHTML":
        return f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) {browser_name}/{version}.0"

    if engine == "Custom":
        if "googlebot-image" in b:
            return f"Googlebot-Image/{version}.1 (+http://www.google.com/bot.html)"
        if "googlebot-news" in b:
            return f"Googlebot-News/{version}.1"
        if "googlebot-video" in b:
            return f"Googlebot-Video/{version}.1"
        if "googlebot" in b:
            return f"Mozilla/5.0 (compatible; Googlebot/{version}.1; +http://www.google.com/bot.html)"
        if "bingbot" in b:
            return f"Mozilla/5.0 (compatible; bingbot/{version}.0; +http://www.bing.com/bingbot.htm)"
        if "yandexbot" in b:
            return f"Mozilla/5.0 (compatible; YandexBot/{version}.0; +http://yandex.com/bots)"
        if "duckduck" in b:
            return f"DuckDuckBot/{version}.0; (+http://duckduckgo.com/duckduckbot.html)"
        if "baidu" in b:
            return f"Mozilla/5.0 (compatible; Baiduspider/{version}.0; +http://www.baidu.com/search/spider.html)"
        if "sogou" in b:
            return f"Sogou web spider/{version}.0"
        if "exabot" in b:
            return f"Mozilla/5.0 (compatible; Exabot/{version}.0; +http://www.exabot.com/go/robot)"
        if "applebot" in b:
            return f"Mozilla/5.0 (compatible; Applebot/{version}.0; +http://www.apple.com/go/applebot)"
        if "facebook" in b:
            return f"facebookexternalhit/{version}.0 (+http://www.facebook.com/externalhit_uatext.php)"
        if "twitter" in b:
            return f"Twitterbot/{version}.0"
        if "linkedin" in b:
            return f"LinkedInBot/{version}.0"
        if "slackbot" in b:
            return f"Slackbot-LinkExpanding {version}.0 (+https://api.slack.com/robots)"
        if "telegram" in b:
            return f"TelegramBot (like TwitterBot)"
        if "discordbot" in b:
            return f"Mozilla/5.0 (compatible; Discordbot/{version}.0; +https://discordapp.com)"
        if "pinterest" in b:
            return f"Mozilla/5.0 (compatible; Pinterestbot/{version}.0; +https://www.pinterest.com/bot.html)"
        if "ahrefs" in b:
            return f"Mozilla/5.0 (compatible; AhrefsBot/{version}.0; +http://ahrefs.com/robot/)"
        if "semrush" in b:
            return f"Mozilla/5.0 (compatible; SemrushBot/{version}.0; +http://www.semrush.com/bot.html)"
        if "mj12" in b:
            return f"Mozilla/5.0 (compatible; MJ12bot/v{version}.0; http://mj12bot.com/)"
        return f"{browser_name}/{version}.0"

    if engine == "CLI":
        if "axios" in b:
            return f"axios/{version}.6.2"
        if "python" in b:
            return f"python-requests/{version}.31.0"
        if "go-http" in b:
            return f"Go-http-client/{version}.1"
        if "java" in b:
            return f"Java/{version}.0.1"
        if "node-fetch" in b:
            return f"node-fetch/{version}.3.3"
        if "okhttp" in b:
            return f"okhttp/{version}.0.0"
        if "postmanruntime" in b:
            return f"PostmanRuntime/{version}.40.0"
        if "google-http-java" in b:
            return f"Google-HTTP-Java-Client/{version}.43.0"
        if "libwww" in b:
            return f"libwww-perl/{version}.72"
        if "curl" in b:
            return f"curl/{version}.12.0"
        if "wget" in b:
            return f"Wget/{version}.21.4"
        if "httpie" in b:
            return f"HTTPie/{version}.2.1"
        return f"{browser_name}/{version}.0"

    if engine == "Text":
        return f"{browser_name}/{version}.0 (text-mode)"

    return f"Mozilla/5.0 ({platform}) {browser_name}/{version}.0"


def is_compatible(browser, os_family):
    b = browser.lower()
    if "safari" in b and "mobile" not in b and "tp" not in b and "webkit" not in b:
        return os_family in ("macOS", "iOS")
    if "mobile-safari" in b:
        return os_family == "iOS"
    if "samsung" in b and os_family != "Android":
        return False
    if "android-webview" in b and os_family != "Android":
        return False
    if "ios-webview" in b and os_family != "iOS":
        return False
    if "uc-browser" in b and os_family not in ("Android", "iOS"):
        return False
    if "duckduckgo" in b and os_family not in ("Android", "iOS", "Windows", "macOS", "Linux"):
        return False
    if "chrome-mobile" in b and os_family not in ("Android", "iOS"):
        return False
    if "firefox-mobile" in b and os_family not in ("Android", "iOS"):
        return False
    return True


def cleanup_old_snapshots(root_dir, keep_days=0.05):
    if not root_dir.exists():
        return

    skip = {".github", "scripts", ".git", "requirements.txt", "README.md", ".gitignore", "releases"}
    skip.update(OPERATING_SYSTEMS.keys())

    snapshots = []
    for item in root_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name in skip:
            continue
        if item.name.startswith("."):
            continue
        try:
            dt = datetime.strptime(item.name, "%Y-%m-%d_%H-%M-%S").replace(tzinfo=timezone.utc)
            snapshots.append((dt, item))
        except ValueError:
            continue

    snapshots.sort(key=lambda x: x[0])
    cutoff = datetime.now(timezone.utc) - timedelta(days=keep_days)

    removed = []
    for dt, folder in snapshots:
        if dt < cutoff:
            shutil.rmtree(folder, ignore_errors=True)
            removed.append(folder.name)

    if removed:
        print(f"Removed old snapshots: {len(removed)}")
    else:
        print(f"Nothing to remove (limit: {keep_days} days)")

    max_snapshots = int(keep_days * 24 * 12) + 5
    remaining = [(dt, f) for dt, f in snapshots if f.name not in removed]
    if len(remaining) > max_snapshots:
        remaining.sort(key=lambda x: x[0])
        extra = len(remaining) - max_snapshots
        for dt, folder in remaining[:extra]:
            shutil.rmtree(folder, ignore_errors=True)
            print(f"Extra cleanup: {folder.name}")


def update_cumulative(root_dir, all_ua):
    root_dir.mkdir(parents=True, exist_ok=True)

    if ALL_SEPARATE_FILES:
        for (os_name, browser_name), ua_list in all_ua.items():
            folder = root_dir / os_name / browser_name
            folder.mkdir(parents=True, exist_ok=True)
            file_path = folder / "agents.txt"

            existing = set()
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            existing.add(line)

            new_ua = [ua for ua in ua_list if ua not in existing]
            if new_ua:
                with open(file_path, "a", encoding="utf-8") as f:
                    for ua in new_ua:
                        f.write(ua + "\n")

    stats_file = root_dir / "stats.txt"
    with open(stats_file, "w", encoding="utf-8") as f:
        f.write(f"Last updated: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"OS/Browser combos: {len(all_ua)}\n")


def build_release_archives(snapshot_dir, releases_dir, timestamp):
    releases_dir.mkdir(parents=True, exist_ok=True)

    zip_path = releases_dir / f"{timestamp}.zip"
    rar_path = releases_dir / f"{timestamp}.rar"
    txt_path = releases_dir / f"{timestamp}.txt"

    os_counts = {}
    total = 0

    for os_folder in sorted(snapshot_dir.iterdir()):
        if not os_folder.is_dir():
            continue
        os_total = 0
        for browser_folder in sorted(os_folder.iterdir()):
            if not browser_folder.is_dir():
                continue
            for txt in browser_folder.glob("*.txt"):
                try:
                    with open(txt, "r", encoding="utf-8") as f:
                        lines = [l for l in f if l.strip()]
                    os_total += len(lines)
                except Exception:
                    continue
        os_counts[os_folder.name] = os_total
        total += os_total

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in snapshot_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(snapshot_dir))

    rar_created = False
    try:
        subprocess.run(
            ["bash", "-c",
             "mkdir -p /tmp/rar && "
             "curl -sL https://www.rarlab.com/rar/rarlinux-x64-624.tar.gz | tar -xz -C /tmp/rar --strip-components=1"],
            check=False,
        )
        rar_bin = "/tmp/rar/rar"
        if Path(rar_bin).exists():
            subprocess.run(
                [rar_bin, "a", "-r", "-ep1", "-m5", "-idq", str(rar_path), "."],
                cwd=snapshot_dir,
                check=True,
            )
            rar_created = True
    except Exception as e:
        print(f"RAR creation failed: {e}")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Snapshot: {timestamp}\n")
        f.write(f"Total UA: {total}\n")
        f.write(f"OS count: {len(os_counts)}\n\n")
        f.write("Per-OS totals:\n")
        for os_name, count in sorted(os_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {os_name}: {count}\n")

    return zip_path, rar_path if rar_created else None, total, os_counts


def build_release_description(timestamp, total, os_counts, zip_name, rar_name):
    lines = []
    lines.append(f"# Snapshot {timestamp}")
    lines.append("")
    lines.append(f"**Total User-Agents:** {total}")
    lines.append(f"**Operating Systems:** {len(os_counts)}")
    lines.append("")
    lines.append("## Downloads")
    lines.append("")
    lines.append(f"- `{zip_name}` - ZIP archive")
    if rar_name:
        lines.append(f"- `{rar_name}` - RAR archive")
    lines.append("")
    lines.append("## Per-OS User-Agent counts")
    lines.append("")
    lines.append("| Operating System | User-Agents |")
    lines.append("|---|---|")
    for os_name, count in sorted(os_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {os_name} | {count} |")
    lines.append("")
    lines.append("## Archive structure")
    lines.append("")
    lines.append("```")
    lines.append(f"{timestamp}/")
    lines.append("  <OS>/")
    lines.append("    <Browser>/")
    lines.append("      agents_1.txt")
    lines.append("      agents_2.txt")
    lines.append("      ...")
    lines.append("```")
    return "\n".join(lines)


def cleanup_old_releases(releases_dir, keep=5):
    if not releases_dir.exists():
        return
    zips = sorted(releases_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    rars = sorted(releases_dir.glob("*.rar"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in zips[keep:]:
        old.unlink(missing_ok=True)
    for old in rars[keep:]:
        old.unlink(missing_ok=True)


def main():
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    root_dir = Path(".")
    releases_dir = root_dir / "releases"

    print(f"Retention: {KEEP_DAYS} days")
    cleanup_old_snapshots(root_dir, keep_days=KEEP_DAYS)

    run_dir = root_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    total_ua = 0
    total_files = 0
    all_ua = defaultdict(list)

    for os_name, os_info in OPERATING_SYSTEMS.items():
        os_folder = run_dir / os_name
        os_folder.mkdir(parents=True, exist_ok=True)

        for browser_name, browser_info in BROWSERS.items():
            if not is_compatible(browser_name, os_info["family"]):
                continue

            browser_folder = os_folder / browser_name
            browser_folder.mkdir(parents=True, exist_ok=True)

            pop = browser_info["popularity"]
            if pop >= 50:
                count = 100
            elif pop >= 10:
                count = 50
            elif pop >= 3:
                count = 30
            else:
                count = 20

            ua_list = []
            seen = set()
            attempts = 0
            max_attempts = count * 20
            while len(ua_list) < count and attempts < max_attempts:
                attempts += 1
                version = pick_version(browser_info)
                ua = build_ua(browser_name, version, os_name, os_info)
                if ua in seen:
                    continue
                seen.add(ua)
                ua_list.append(ua)

            file_index = 1
            for i in range(0, len(ua_list), BATCH_SIZE):
                chunk = ua_list[i:i + BATCH_SIZE]
                txt_file = browser_folder / f"agents_{file_index}.txt"
                with open(txt_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(chunk))
                    f.write("\n")
                file_index += 1
                total_files += 1

            all_ua[(os_name, browser_name)].extend(ua_list)
            total_ua += len(ua_list)

    print(f"Updating cumulative folders...")
    update_cumulative(root_dir, all_ua)

    print(f"Building release archives...")
    zip_path, rar_path, total_from_zip, os_counts = build_release_archives(run_dir, releases_dir, timestamp)

    desc = build_release_description(
        timestamp,
        total_from_zip,
        os_counts,
        zip_path.name,
        rar_path.name if rar_path else None,
    )
    desc_path = releases_dir / f"{timestamp}.md"
    with open(desc_path, "w", encoding="utf-8") as f:
        f.write(desc)

    print(f"Cleaning old releases...")
    cleanup_old_releases(releases_dir, keep=RELEASE_KEEP)

    print(f"Generated UA: {total_ua}")
    print(f"Files in snapshot: {total_files}")
    print(f"Total UA in release: {total_from_zip}")
    print(f"OS count: {len(OPERATING_SYSTEMS)}")
    print(f"Browser count: {len(BROWSERS)}")
    print(f"Snapshot: {run_dir}")
    print(f"ZIP: {zip_path}")
    print(f"RAR: {rar_path if rar_path else 'not created'}")


if __name__ == "__main__":
    main()
