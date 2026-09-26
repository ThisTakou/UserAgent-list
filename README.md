# UserAgent List

Автоматически обновляемая база User-Agent строк для 100+ браузеров на 100+ операционных системах.

[English](#english) | [Русский](#русский) | [Deutsch](#deutsch) | [Español](#español) | [中文](#中文) | [日本語](#日本語) | [Français](#français) | [Italiano](#italiano) | [Português](#português) | [한국어](#한국어)

# 💸 Поддержка проекта

**Gram (TON):** `UQCXJEpjngpV1bx5TYuYbdUOMzewSUSu4ruTy3kO0Qq4FDqW` | **RU-Card:** `2204321297371965`

<img width="1870" height="841" alt="image" src="https://github.com/user-attachments/assets/36669e43-b7dd-478b-8890-7ee9cd1f8760" />


---

## English

### Overview

This repository automatically generates and maintains a database of User-Agent strings. The generator runs on GitHub Actions and updates every 5 minutes. All User-Agent strings are grouped by operating system and browser, organized into timestamped snapshot folders.

### Features

- 100+ browsers: Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor, and others
- 100+ operating systems: Windows, macOS, Linux, Android, iOS, Chrome OS, BSD, and others
- Weighted generation: popular browsers and fresh versions appear more frequently
- Realistic combinations: Safari does not appear on Windows, Samsung Internet only on Android
- Cumulative database: unique User-Agents collected in the `data/ALL/` folder
- Auto cleanup: snapshots older than the retention window are removed
- Update interval: every 5 minutes

### Repository Structure

```
data/
├── 2025-01-15_14-05-03/
│   ├── Windows-11/
│   │   ├── Chrome/
│   │   │   ├── agents_1.txt
│   │   │   ├── agents_2.txt
│   │   │   └── agents_3.txt
│   │   ├── Firefox/
│   │   └── Edge/
│   ├── macOS-15-Sequoia/
│   ├── iOS-17/
│   ├── Android-14/
│   └── ...
├── 2025-01-15_14-10-47/
├── ...
└── ALL/
    ├── Windows-11/
    │   └── Chrome/
    │       └── agents.txt
    ├── all_user_agents.txt
    └── stats.txt
```

### File Format

Each `.txt` file contains User-Agent strings, one per line. No headers, no JSON, no extra content.

Example from `data/2025-01-15_14-05-03/Windows-11/Chrome/agents_1.txt`:

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.4521.78 Safari/537.36
```

### Usage

Direct raw URL:

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Python example:

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

Bash example:

```bash
curl -s https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt | shuf -n 1
```

### Statistics

Current statistics are available in `data/ALL/stats.txt`:

```
Last updated: 2025-01-15T14:05:03+00:00
Total unique UA: 152340
Added this run: 4218
OS/Browser combos: 1840
```

### Configuration

All settings are located at the top of `scripts/generate.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `KEEP_HOURS` | 24 | How many hours of snapshots to keep |
| `BATCH_SIZE` | 1 | User-Agents per file |
| `ALL_SEPARATE_FILES` | True | Split `ALL/` by OS and browser |

Update interval is defined in `.github/workflows/generate.yml`:

```yaml
schedule:
  - cron: '*/5 * * * *'
```

### How It Works

1. GitHub Actions triggers the workflow every 5 minutes
2. Python script generates User-Agent strings based on weighted popularity
3. Snapshot is saved to `data/YYYY-MM-DD_HH-MM-SS/`
4. Cumulative database in `data/ALL/` is updated with new unique entries
5. Snapshots older than `KEEP_HOURS` are deleted
6. Changes are committed and pushed automatically

### License

MIT

[Back to top](#useragent-list)

---

## Русский

### Обзор

Репозиторий автоматически генерирует и поддерживает базу User-Agent строк. Генератор работает через GitHub Actions и обновляется каждые 5 минут. Все строки сгруппированы по операционной системе и браузеру, разложены по папкам с временными метками.

### Возможности

- 100+ браузеров: Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor и другие
- 100+ операционных систем: Windows, macOS, Linux, Android, iOS, Chrome OS, BSD и другие
- Взвешенная генерация: популярные браузеры и свежие версии выпадают чаще
- Реалистичные комбинации: Safari не появляется на Windows, Samsung Internet только на Android
- Накопительная база: уникальные User-Agent собираются в папке `data/ALL/`
- Автоочистка: снапшоты старше заданного окна удаляются
- Интервал обновления: каждые 5 минут

### Структура репозитория

```
data/
├── 2025-01-15_14-05-03/
│   ├── Windows-11/
│   │   ├── Chrome/
│   │   │   ├── agents_1.txt
│   │   │   ├── agents_2.txt
│   │   │   └── agents_3.txt
│   │   ├── Firefox/
│   │   └── Edge/
│   ├── macOS-15-Sequoia/
│   ├── iOS-17/
│   ├── Android-14/
│   └── ...
├── 2025-01-15_14-10-47/
├── ...
└── ALL/
    ├── Windows-11/
    │   └── Chrome/
    │       └── agents.txt
    ├── all_user_agents.txt
    └── stats.txt
```

### Формат файлов

Каждый `.txt` файл содержит строки User-Agent, по одной на строку. Ни заголовков, ни JSON, ни лишнего содержимого.

Пример из `data/2025-01-15_14-05-03/Windows-11/Chrome/agents_1.txt`:

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.4521.78 Safari/537.36
```

### Использование

Прямая ссылка на raw файл:

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Пример на Python:

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

Пример на Bash:

```bash
curl -s https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt | shuf -n 1
```

### Статистика

Актуальная статистика доступна в `data/ALL/stats.txt`:

```
Last updated: 2025-01-15T14:05:03+00:00
Total unique UA: 152340
Added this run: 4218
OS/Browser combos: 1840
```

### Настройка

Все параметры находятся в начале `scripts/generate.py`:

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `KEEP_HOURS` | 24 | Сколько часов хранить снапшоты |
| `BATCH_SIZE` | 1 | User-Agent в одном файле |
| `ALL_SEPARATE_FILES` | True | Разбивать `ALL/` по ОС и браузеру |

Интервал обновления задаётся в `.github/workflows/generate.yml`:

```yaml
schedule:
  - cron: '*/5 * * * *'
```

### Как работает

1. GitHub Actions запускает workflow каждые 5 минут
2. Python скрипт генерирует User-Agent строки на основе взвешенной популярности
3. Снапшот сохраняется в `data/YYYY-MM-DD_HH-MM-SS/`
4. Накопительная база в `data/ALL/` пополняется новыми уникальными записями
5. Снапшоты старше `KEEP_HOURS` удаляются
6. Изменения коммитятся и пушатся автоматически

### Лицензия

MIT

[Наверх](#useragent-list)

---

## Deutsch

### Überblick

Dieses Repository generiert und pflegt automatisch eine Datenbank mit User-Agent-Zeichenfolgen. Der Generator läuft über GitHub Actions und aktualisiert alle 5 Minuten. Alle User-Agent-Zeichenfolgen sind nach Betriebssystem und Browser gruppiert und in Zeitstempelordnern organisiert.

### Funktionen

- Über 100 Browser: Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor und andere
- Über 100 Betriebssysteme: Windows, macOS, Linux, Android, iOS, Chrome OS, BSD und andere
- Gewichtete Generierung: beliebte Browser und aktuelle Versionen erscheinen häufiger
- Realistische Kombinationen: Safari erscheint nicht unter Windows, Samsung Internet nur unter Android
- Kumulative Datenbank: einzigartige User-Agents werden im Ordner `data/ALL/` gesammelt
- Automatische Bereinigung: Schnappschüsse, die älter als das Aufbewahrungsfenster sind, werden entfernt
- Aktualisierungsintervall: alle 5 Minuten

### Verwendung

Direkte Raw-URL:

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Python-Beispiel:

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### Lizenz

MIT

[Zurück nach oben](#useragent-list)

---

## Español

### Descripción general

Este repositorio genera y mantiene automáticamente una base de datos de cadenas User-Agent. El generador se ejecuta en GitHub Actions y se actualiza cada 5 minutos. Todas las cadenas User-Agent están agrupadas por sistema operativo y navegador, organizadas en carpetas con marca de tiempo.

### Características

- Más de 100 navegadores: Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor y otros
- Más de 100 sistemas operativos: Windows, macOS, Linux, Android, iOS, Chrome OS, BSD y otros
- Generación ponderada: los navegadores populares y las versiones recientes aparecen con más frecuencia
- Combinaciones realistas: Safari no aparece en Windows, Samsung Internet solo en Android
- Base de datos acumulativa: los User-Agents únicos se recopilan en la carpeta `data/ALL/`
- Limpieza automática: las instantáneas más antiguas que la ventana de retención se eliminan
- Intervalo de actualización: cada 5 minutos

### Uso

URL raw directa:

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Ejemplo en Python:

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### Licencia

MIT

[Volver arriba](#useragent-list)

---

## 中文

### 概述

本仓库自动生成并维护一个 User-Agent 字符串数据库。生成器通过 GitHub Actions 运行，每 5 分钟更新一次。所有 User-Agent 字符串按操作系统和浏览器分组，存放在带时间戳的文件夹中。

### 功能

- 100+ 种浏览器：Chrome、Firefox、Safari、Edge、Opera、Brave、Vivaldi、Yandex、Tor 等
- 100+ 种操作系统：Windows、macOS、Linux、Android、iOS、Chrome OS、BSD 等
- 加权生成：流行的浏览器和较新的版本出现频率更高
- 真实组合：Safari 不会出现在 Windows 上，Samsung Internet 仅在 Android 上
- 累积数据库：唯一的 User-Agent 收集在 `data/ALL/` 文件夹中
- 自动清理：超过保留窗口的快照会被删除
- 更新间隔：每 5 分钟

### 使用方法

直接使用 raw URL：

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Python 示例：

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### 许可证

MIT

[返回顶部](#useragent-list)

---

## 日本語

### 概要

このリポジトリは、User-Agent 文字列のデータベースを自動的に生成および維持します。ジェネレーターは GitHub Actions 上で実行され、5 分ごとに更新されます。すべての User-Agent 文字列は、オペレーティングシステムとブラウザごとにグループ化され、タイムスタンプ付きのフォルダーに整理されています。

### 機能

- 100 以上のブラウザ：Chrome、Firefox、Safari、Edge、Opera、Brave、Vivaldi、Yandex、Tor など
- 100 以上のオペレーティングシステム：Windows、macOS、Linux、Android、iOS、Chrome OS、BSD など
- 重み付け生成：人気のあるブラウザと新しいバージョンがより頻繁に表示されます
- 現実的な組み合わせ：Safari は Windows に表示されず、Samsung Internet は Android のみ
- 累積データベース：一意の User-Agent は `data/ALL/` フォルダーに収集されます
- 自動クリーンアップ：保持期間を超えたスナップショットが削除されます
- 更新間隔：5 分ごと

### 使用法

直接 raw URL：

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Python の例：

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### ライセンス

MIT

[トップへ戻る](#useragent-list)

---

## Français

### Aperçu

Ce dépôt génère et maintient automatiquement une base de données de chaînes User-Agent. Le générateur s'exécute sur GitHub Actions et se met à jour toutes les 5 minutes. Toutes les chaînes User-Agent sont regroupées par système d'exploitation et par navigateur, organisées dans des dossiers horodatés.

### Fonctionnalités

- Plus de 100 navigateurs : Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor et autres
- Plus de 100 systèmes d'exploitation : Windows, macOS, Linux, Android, iOS, Chrome OS, BSD et autres
- Génération pondérée : les navigateurs populaires et les versions récentes apparaissent plus fréquemment
- Combinaisons réalistes : Safari n'apparaît pas sous Windows, Samsung Internet uniquement sous Android
- Base de données cumulative : les User-Agents uniques sont collectés dans le dossier `data/ALL/`
- Nettoyage automatique : les instantanés plus anciens que la fenêtre de rétention sont supprimés
- Intervalle de mise à jour : toutes les 5 minutes

### Utilisation

URL raw directe :

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Exemple Python :

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### Licence

MIT

[Retour en haut](#useragent-list)

---

## Italiano

### Panoramica

Questo repository genera e mantiene automaticamente un database di stringhe User-Agent. Il generatore viene eseguito su GitHub Actions e si aggiorna ogni 5 minuti. Tutte le stringhe User-Agent sono raggruppate per sistema operativo e browser, organizzate in cartelle con timestamp.

### Caratteristiche

- Oltre 100 browser: Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor e altri
- Oltre 100 sistemi operativi: Windows, macOS, Linux, Android, iOS, Chrome OS, BSD e altri
- Generazione ponderata: i browser popolari e le versioni recenti appaiono più frequentemente
- Combinazioni realistiche: Safari non appare su Windows, Samsung Internet solo su Android
- Database cumulativo: gli User-Agent unici vengono raccolti nella cartella `data/ALL/`
- Pulizia automatica: gli snapshot più vecchi della finestra di conservazione vengono rimossi
- Intervallo di aggiornamento: ogni 5 minuti

### Utilizzo

URL raw diretto:

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Esempio Python:

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### Licenza

MIT

[Torna in alto](#useragent-list)

---

## Português

### Visão geral

Este repositório gera e mantém automaticamente um banco de dados de strings User-Agent. O gerador é executado no GitHub Actions e é atualizado a cada 5 minutos. Todas as strings User-Agent são agrupadas por sistema operacional e navegador, organizadas em pastas com timestamp.

### Recursos

- Mais de 100 navegadores: Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor e outros
- Mais de 100 sistemas operacionais: Windows, macOS, Linux, Android, iOS, Chrome OS, BSD e outros
- Geração ponderada: navegadores populares e versões recentes aparecem com mais frequência
- Combinações realistas: Safari não aparece no Windows, Samsung Internet apenas no Android
- Banco de dados cumulativo: User-Agents únicos são coletados na pasta `data/ALL/`
- Limpeza automática: instantâneos mais antigos que a janela de retenção são removidos
- Intervalo de atualização: a cada 5 minutos

### Uso

URL raw direta:

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Exemplo em Python:

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### Licença

MIT

[Voltar ao topo](#useragent-list)

---

## 한국어

### 개요

이 저장소는 User-Agent 문자열 데이터베이스를 자동으로 생성하고 유지합니다. 생성기는 GitHub Actions에서 실행되며 5분마다 업데이트됩니다. 모든 User-Agent 문자열은 운영 체제와 브라우저별로 그룹화되어 타임스탬프 폴더에 정리됩니다.

### 기능

- 100개 이상의 브라우저: Chrome, Firefox, Safari, Edge, Opera, Brave, Vivaldi, Yandex, Tor 등
- 100개 이상의 운영 체제: Windows, macOS, Linux, Android, iOS, Chrome OS, BSD 등
- 가중 생성: 인기 있는 브라우저와 최신 버전이 더 자주 나타납니다
- 현실적인 조합: Safari는 Windows에 나타나지 않고 Samsung Internet은 Android에만 나타납니다
- 누적 데이터베이스: 고유한 User-Agent는 `data/ALL/` 폴더에 수집됩니다
- 자동 정리: 보존 기간보다 오래된 스냅샷이 제거됩니다
- 업데이트 간격: 5분마다

### 사용법

직접 raw URL:

```
https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt
```

Python 예제:

```python
import urllib.request
import random

URL = "https://raw.githubusercontent.com/ThisTakou/UserAgent-list/main/data/ALL/all_user_agents.txt"

with urllib.request.urlopen(URL) as response:
    agents = [line.strip() for line in response if line.strip()]

print(random.choice(agents))
```

### 라이선스

MIT

[맨 위로](#useragent-list)

---

## License

MIT License

Copyright (c) 2026 ThisTakou

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
