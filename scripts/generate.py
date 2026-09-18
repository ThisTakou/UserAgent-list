#!/usr/bin/env python3
"""
Random User-Agent Generator v3
- Взвешенная генерация по популярности
- .txt файлы содержат ТОЛЬКО строки User-Agent (по одному в строке)
- Структура: data/<timestamp>/<OS>/<Browser>/agents_N.txt
- Автоочистка старых данных
"""

import random
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ============================================================
# БРАУЗЕРЫ С ВЕСАМИ ПОПУЛЯРНОСТИ
# ============================================================

def weighted_versions(latest: int, supported: int):
    """Реалистичное распределение: свежие версии популярнее."""
    versions = []
    for v in range(supported, latest + 1):
        d = latest - v
        w = 40 if d == 0 else 25 if d == 1 else 15 if d == 2 else 8 if d == 3 else 3 if d <= 6 else 1
        versions.append((v, w))
    return versions


BROWSERS = {
    # Chrome family
    "Chrome":              {"engine": "Blink",   "popularity": 65, "versions": weighted_versions(131, 120)},
    "Chrome-Beta":         {"engine": "Blink",   "popularity": 1,  "versions": [(132, 1)]},
    "Chrome-Canary":       {"engine": "Blink",   "popularity": 1,  "versions": [(133, 1)]},
    "Chrome-Dev":          {"engine": "Blink",   "popularity": 1,  "versions": [(132, 1)]},
    "Chromium":            {"engine": "Blink",   "popularity": 2,  "versions": weighted_versions(131, 120)},
    "Ungoogled-Chromium":  {"engine": "Blink",   "popularity": 1,  "versions": weighted_versions(131, 120)},

    # Safari
    "Safari":              {"engine": "WebKit",  "popularity": 18, "versions": [(18, 40), (17, 35), (16, 15), (15, 7), (14, 3)]},
    "Mobile-Safari":       {"engine": "WebKit",  "popularity": 10, "versions": [(18, 40), (17, 35), (16, 15), (15, 7), (14, 3)]},

    # Edge
    "Edge":                {"engine": "Blink",   "popularity": 5,  "versions": weighted_versions(131, 120)},
    "Edge-Beta":           {"engine": "Blink",   "popularity": 1,  "versions": [(132, 1)]},

    # Firefox
    "Firefox":             {"engine": "Gecko",   "popularity": 3,  "versions": weighted_versions(134, 128)},
    "Firefox-ESR":         {"engine": "Gecko",   "popularity": 1,  "versions": [(128, 3), (115, 1)]},
    "Firefox-Beta":        {"engine": "Gecko",   "popularity": 1,  "versions": [(135, 1)]},
    "Firefox-Nightly":     {"engine": "Gecko",   "popularity": 1,  "versions": [(136, 1)]},
    "Firefox-Developer":   {"engine": "Gecko",   "popularity": 1,  "versions": [(134, 1)]},

    # Opera
    "Opera":               {"engine": "Blink",   "popularity": 2,  "versions": weighted_versions(116, 105)},
    "Opera-GX":            {"engine": "Blink",   "popularity": 1,  "versions": weighted_versions(116, 105)},
    "Opera-Air":           {"engine": "Blink",   "popularity": 1,  "versions": [(4, 1), (3, 1)]},

    # Brave / Vivaldi / Yandex
    "Brave":               {"engine": "Blink",   "popularity": 1,  "versions": weighted_versions(131, 120)},
    "Brave-Nightly":       {"engine": "Blink",   "popularity": 1,  "versions": [(133, 1)]},
    "Vivaldi":             {"engine": "Blink",   "popularity": 1,  "versions": [(7, 3), (6, 1)]},
    "Vivaldi-Snapshot":    {"engine": "Blink",   "popularity": 1,  "versions": [(8, 1)]},
    "Yandex":              {"engine": "Blink",   "popularity": 1,  "versions": weighted_versions(25, 23)},

    # Mobile
    "Samsung-Internet":    {"engine": "Blink",   "popularity": 2,  "versions": weighted_versions(26, 22)},
    "UC-Browser":          {"engine": "Blink",   "popularity": 1,  "versions": [(13, 3), (12, 1)]},
    "DuckDuckGo":          {"engine": "Blink",   "popularity": 1,  "versions": [(7, 2), (6, 1)]},
    "Android-WebView":     {"engine": "Blink",   "popularity": 1,  "versions": weighted_versions(131, 120)},
    "iOS-WebView":         {"engine": "WebKit",  "popularity": 1,  "versions": [(18, 3), (17, 2), (16, 1)]},

    # Privacy
    "Tor-Browser":         {"engine": "Gecko",   "popularity": 1,  "versions": [(14, 3), (13, 2), (12, 1)]},
    "Mullvad-Browser":     {"engine": "Gecko",   "popularity": 1,  "versions": [(14, 2), (13, 1)]},
    "LibreWolf":           {"engine": "Gecko",   "popularity": 1,  "versions": weighted_versions(134, 128)},
    "Waterfox":            {"engine": "Gecko",   "popularity": 1,  "versions": [(6, 2), (5, 1)]},

    # Exotic
    "Pale-Moon":           {"engine": "Goanna",  "popularity": 1,  "versions": [(33, 2), (32, 1), (31, 1)]},
    "Basilisk":            {"engine": "Goanna",  "popularity": 1,  "versions": [(2025, 1), (2024, 1)]},
    "SeaMonkey":           {"engine": "Gecko",   "popularity": 1,  "versions": [(2, 1)]},
    "Falkon":              {"engine": "WebKit",  "popularity": 1,  "versions": [(3, 1), (2, 1)]},
    "Konqueror":           {"engine": "KHTML",   "popularity": 1,  "versions": [(24, 2), (23, 1)]},
    "Epiphany":            {"engine": "WebKit",  "popularity": 1,  "versions": [(46, 2), (45, 1)]},
    "Midori":              {"engine": "WebKit",  "popularity": 1,  "versions": [(11, 1), (10, 1)]},

    # Electron
    "Electron":            {"engine": "Electron", "popularity": 1, "versions": weighted_versions(33, 28)},
    "Discord":             {"engine": "Electron", "popularity": 1, "versions": [(1, 1)]},
    "Slack":               {"engine": "Electron", "popularity": 1, "versions": [(4, 1)]},
    "Spotify":             {"engine": "Electron", "popularity": 1, "versions": [(1, 1)]},
    "WhatsApp-Desktop":    {"engine": "Electron", "popularity": 1, "versions": [(2, 1)]},
    "Telegram-Desktop":    {"engine": "Electron", "popularity": 1, "versions": [(5, 1), (4, 1)]},
    "Signal-Desktop":      {"engine": "Electron", "popularity": 1, "versions": [(7, 1), (6, 1)]},
    "Postman":             {"engine": "Electron", "popularity": 1, "versions": [(11, 2), (10, 1)]},
    "Insomnia":            {"engine": "Electron", "popularity": 1, "versions": [(2025, 1), (2024, 1)]},

    # Bots
    "Googlebot":           {"engine": "Custom", "popularity": 1, "versions": [(2, 1)]},
    "Googlebot-Image":     {"engine": "Custom", "popularity": 1, "versions": [(2, 1)]},
    "Bingbot":             {"engine": "Custom", "popularity": 1, "versions": [(2, 1)]},
    "YandexBot":           {"engine": "Custom", "popularity": 1, "versions": [(3, 1)]},
    "DuckDuckBot":         {"engine": "Custom", "popularity": 1, "versions": [(1, 1)]},
    "Baiduspider":         {"engine": "Custom", "popularity": 1, "versions": [(2, 1)]},
    "Applebot":            {"engine": "Custom", "popularity": 1, "versions": [(1, 1)]},
    "facebookexternalhit": {"engine": "Custom", "popularity": 1, "versions": [(1, 1)]},
    "Twitterbot":          {"engine": "Custom", "popularity": 1, "versions": [(1, 1)]},
    "LinkedInBot":         {"engine": "Custom", "popularity": 1, "versions": [(1, 1)]},
    "TelegramBot":         {"engine": "Custom", "popularity": 1, "versions": [(1, 1)]},

    # CLI
    "Curl":                {"engine": "CLI", "popularity": 1, "versions": [(8, 3), (7, 1)]},
    "Wget":                {"engine": "CLI", "popularity": 1, "versions": [(1, 1)]},
    "HTTPie":              {"engine": "CLI", "popularity": 1, "versions": [(3, 1)]},

    # Text
    "Lynx":                {"engine": "Text", "popularity": 1, "versions": [(2, 2), (2.9, 1)]},
    "w3m":                 {"engine": "Text", "popularity": 1, "versions": [(0.5, 1)]},
    "ELinks":              {"engine": "Text", "popularity": 1, "versions": [(0.13, 1)]},
    "Links":               {"engine": "Text", "popularity": 1, "versions": [(2.29, 1)]},
}

# ============================================================
# ОС С ВЕСАМИ ПОПУЛЯРНОСТИ
# ============================================================
OPERATING_SYSTEMS = {
    # Windows
    "Windows-11":           {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 40},
    "Windows-10":           {"platform_tpl": "Windows NT 10.0; Win64; x64", "family": "Windows", "popularity": 30},
    "Windows-8.1":          {"platform_tpl": "Windows NT 6.3; Win64; x64",  "family": "Windows", "popularity": 1},
    "Windows-7":            {"platform_tpl": "Windows NT 6.1; Win64; x64",  "family": "Windows", "popularity": 1},

    # macOS
    "macOS-15-Sequoia":     {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 6},
    "macOS-14-Sonoma":      {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 5},
    "macOS-13-Ventura":     {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 3},
    "macOS-12-Monterey":    {"platform_tpl": "Macintosh; Intel Mac OS X 10_15_7", "family": "macOS", "popularity": 2},
    "macOS-ARM-M1":         {"platform_tpl": "Macintosh; ARM Mac OS X 11_0_0",    "family": "macOS", "popularity": 2},
    "macOS-ARM-M2":         {"platform_tpl": "Macintosh; ARM Mac OS X 13_0_0",    "family": "macOS", "popularity": 3},
    "macOS-ARM-M3":         {"platform_tpl": "Macintosh; ARM Mac OS X 14_0_0",    "family": "macOS", "popularity": 3},

    # Linux
    "Ubuntu-24.04":         {"platform_tpl": "X11; Ubuntu; Linux x86_64",         "family": "Linux", "popularity": 2},
    "Ubuntu-22.04":         {"platform_tpl": "X11; Ubuntu; Linux x86_64",         "family": "Linux", "popularity": 1},
    "Debian-12":            {"platform_tpl": "X11; Linux x86_64",                 "family": "Linux", "popularity": 1},
    "Fedora-40":            {"platform_tpl": "X11; Fedora; Linux x86_64",         "family": "Linux", "popularity": 1},
    "Arch-Linux":           {"platform_tpl": "X11; Arch Linux; Linux x86_64",     "family": "Linux", "popularity": 1},
    "Linux-Mint":           {"platform_tpl": "X11; Linux Mint; Linux x86_64",     "family": "Linux", "popularity": 1},

    # Android
    "Android-15":           {"platform_tpl": "Linux; Android 15",   "family": "Android", "popularity": 8},
    "Android-14":           {"platform_tpl": "Linux; Android 14",   "family": "Android", "popularity": 10},
    "Android-13":           {"platform_tpl": "Linux; Android 13",   "family": "Android", "popularity": 7},
    "Android-12":           {"platform_tpl": "Linux; Android 12",   "family": "Android", "popularity": 4},
    "Android-11":           {"platform_tpl": "Linux; Android 11",   "family": "Android", "popularity": 3},
    "Android-10":           {"platform_tpl": "Linux; Android 10",   "family": "Android", "popularity": 2},

    # iOS
    "iOS-18":               {"platform_tpl": "iPhone; CPU iPhone OS 18_0 like Mac OS X", "family": "iOS", "popularity": 12},
    "iOS-17":               {"platform_tpl": "iPhone; CPU iPhone OS 17_0 like Mac OS X", "family": "iOS", "popularity": 15},
    "iOS-16":               {"platform_tpl": "iPhone; CPU iPhone OS 16_0 like Mac OS X", "family": "iOS", "popularity": 8},
    "iOS-15":               {"platform_tpl": "iPhone; CPU iPhone OS 15_0 like Mac OS X", "family": "iOS", "popularity": 3},
    "iPadOS-18":            {"platform_tpl": "iPad; CPU OS 18_0 like Mac OS X",          "family": "iOS", "popularity": 4},
    "iPadOS-17":            {"platform_tpl": "iPad; CPU OS 17_0 like Mac OS X",          "family": "iOS", "popularity": 5},
}


# ============================================================
# ГЕНЕРАЦИЯ UA
# ============================================================

def pick_version(browser_info: dict):
    versions = [v for v, w in browser_info["versions"]]
    weights  = [w for v, w in browser_info["versions"]]
    return random.choices(versions, weights=weights, k=1)[0]


def build_ua(browser_name: str, version, os_name: str, os_info: dict) -> str:
    browser_info = BROWSERS[browser_name]
    engine = browser_info["engine"]
    platform = os_info["platform_tpl"]
    b = browser_name.lower()

    # ---- Blink / Electron ----
    if engine in ("Blink", "Electron"):
        chrome_ver = version if b == "chrome" else random.randint(120, 131)

        if "edge" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver}.0.0.0 Safari/537.36 Edg/{chrome_ver}.0.0.0")
        if "opera" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver}.0.0.0 Safari/537.36 OPR/{version}.0.0.0")
        if "vivaldi" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver}.0.0.0 Safari/537.36 Vivaldi/{version}.0")
        if "yandex" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver}.0.0.0 YaBrowser/{version}.0 Safari/537.36")
        if "samsung" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver}.0.0.0 Mobile Safari/537.36 SamsungBrowser/{version}.0")
        if "uc-browser" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Version/{version}.0 UCBrowser/{version}.0.0.0 Mobile Safari/537.36")
        if "duckduckgo" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver}.0.0.0 Safari/537.36 DuckDuckGo/{version}")
        if "brave" in b:
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver}.0.0.0 Safari/537.36")
        if engine == "Electron":
            return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"{browser_name}/{version}.0.0 Chrome/{chrome_ver}.0.0.0 "
                    f"Electron/{version}.0.0 Safari/537.36")

        return (f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_ver}.0.{random.randint(1000,9999)}.{random.randint(50,200)} "
                f"Safari/537.36")

    # ---- Gecko ----
    if engine == "Gecko":
        if any(x in b for x in ["tor", "mullvad", "librewolf", "waterfox"]):
            return (f"Mozilla/5.0 ({platform}; rv:{version}.0) Gecko/20100101 Firefox/{version}.0")
        return (f"Mozilla/5.0 ({platform}; rv:{version}.0) Gecko/20100101 Firefox/{version}.0")

    # ---- Goanna ----
    if engine == "Goanna":
        return (f"Mozilla/5.0 ({platform}; rv:{version}.0) Gecko/20100101 {browser_name}/{version}.0")

    # ---- WebKit ----
    if engine == "WebKit":
        if "mobile" in b or os_info["family"] == "iOS":
            ios_ver = version if version < 100 else random.randint(15, 18)
            return (f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_ver}_0 like Mac OS X) "
                    f"AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ios_ver}.0 "
                    f"Mobile/15E148 Safari/604.1")
        return (f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                f"Version/{version}.0 Safari/605.1.15")

    # ---- KHTML ----
    if engine == "KHTML":
        return (f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                f"{browser_name}/{version}.0")

    # ---- Custom (боты) ----
    if engine == "Custom":
        if "googlebot-image" in b:
            return f"Googlebot-Image/{version}.1 (+http://www.google.com/bot.html)"
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
        if "applebot" in b:
            return f"Mozilla/5.0 (compatible; Applebot/{version}.0; +http://www.apple.com/go/applebot)"
        if "facebook" in b:
            return f"facebookexternalhit/{version}.0 (+http://www.facebook.com/externalhit_uatext.php)"
        if "twitter" in b:
            return f"Twitterbot/{version}.0"
        if "linkedin" in b:
            return f"LinkedInBot/{version}.0"
        if "telegram" in b:
            return f"TelegramBot (like TwitterBot)"
        return f"{browser_name}/{version}.0"

    # ---- CLI ----
    if engine == "CLI":
        return f"{browser_name}/{version}.0"

    # ---- Text ----
    if engine == "Text":
        return f"{browser_name}/{version}.0 (text-mode)"

    return f"Mozilla/5.0 ({platform}) {browser_name}/{version}.0"


def is_compatible(browser: str, os_family: str) -> bool:
    b = browser.lower()
    # Safari только на macOS/iOS
    if "safari" in b and "mobile" not in b:
        return os_family in ("macOS", "iOS")
    if "mobile-safari" in b:
        return os_family == "iOS"
    # Samsung Internet только на Android
    if "samsung" in b and os_family != "Android":
        return False
    # Android WebView только на Android
    if "android-webview" in b and os_family != "Android":
        return False
    # iOS WebView только на iOS
    if "ios-webview" in b and os_family != "iOS":
        return False
    # Мобильные браузеры только на мобильных
    mobile_browsers = ("uc-browser", "duckduckgo")
    if any(x in b for x in mobile_browsers) and os_family not in ("Android", "iOS"):
        return False
    # iOS-специфичное (Mobile Safari) уже проверено
    return True


# ============================================================
# ОЧИСТКА
# ============================================================

def cleanup_old_data(data_dir: Path, keep_days: int = 3):
    """Удаляет папки формата YYYY-MM-DD_HH-MM старше keep_days дней."""
    if not data_dir.exists():
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=keep_days)
    removed = 0

    for item in data_dir.iterdir():
        if not item.is_dir():
            continue
        # Формат: 2025-01-15_14-00
        try:
            folder_dt = datetime.strptime(item.name, "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        except ValueError:
            continue  # не наш формат — пропускаем

        if folder_dt < cutoff:
            shutil.rmtree(item, ignore_errors=True)
            removed += 1

    if removed:
        print(f"🧹 Удалено старых папок: {removed}")
    else:
        print(f"🧹 Нечего удалять (храним {keep_days} дн.)")


# ============================================================
# MAIN
# ============================================================

def main():
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d_%H-%M")   # папка с временем генерации

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # 1) Очистка старых данных
    cleanup_old_data(data_dir, keep_days=3)

    # 2) Папка текущего запуска
    run_dir = data_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    total_ua = 0
    total_files = 0
    total_browsers_used = set()
    total_os_used = set()

    # 3) Проходим по всем ОС
    for os_name, os_info in OPERATING_SYSTEMS.items():
        os_folder = run_dir / os_name
        os_folder.mkdir(parents=True, exist_ok=True)

        # 4) Проходим по всем браузерам (совместимым с этой ОС)
        for browser_name, browser_info in BROWSERS.items():
            if not is_compatible(browser_name, os_info["family"]):
                continue

            browser_folder = os_folder / browser_name
            browser_folder.mkdir(parents=True, exist_ok=True)

            # Сколько UA генерим — по популярности
            pop = browser_info["popularity"]
            if pop >= 50:
                count = 8
            elif pop >= 10:
                count = 5
            elif pop >= 3:
                count = 3
            else:
                count = 2

            # Генерим уникальные UA
            ua_list = []
            seen = set()
            attempts = 0
            while len(ua_list) < count and attempts < count * 10:
                attempts += 1
                version = pick_version(browser_info)
                ua = build_ua(browser_name, version, os_name, os_info)
                if ua in seen:
                    continue
                seen.add(ua)
                ua_list.append(ua)

            # Разбиваем по файлам: по 1 UA на файл для "чистоты" формата,
            # либо пачками. Здесь — по 1 UA на файл (agents_1.txt, agents_2.txt ...)
            # Если хотите по N UA в файле — см. BATCH_SIZE ниже.
            BATCH_SIZE = 1
            file_index = 1
            for i in range(0, len(ua_list), BATCH_SIZE):
                chunk = ua_list[i:i + BATCH_SIZE]
                txt_file = browser_folder / f"agents_{file_index}.txt"
                with open(txt_file, "w", encoding="utf-8") as f:
                    # СТРОГО строки UA, по одному в строке, без заголовков
                    f.write("\n".join(chunk))
                    f.write("\n")
                file_index += 1
                total_files += 1

            total_ua += len(ua_list)
            total_browsers_used.add(browser_name)
            total_os_used.add(os_name)

    # 5) Итоговый отчёт в консоль
    print(f"✅ Сгенерировано UA: {total_ua}")
    print(f"📦 Файлов .txt:      {total_files}")
    print(f"💻 ОС:               {len(total_os_used)}")
    print(f"🌐 Браузеров:        {len(total_browsers_used)}")
    print(f"📂 Путь:             {run_dir}")


if __name__ == "__main__":
    main()
