# How to start

## Быстрый старт (Windows / macOS / Linux)

По сути весь запуск сводится к трём шагам:

1. **Установить Docker** (Docker Desktop на Windows/macOS, docker + docker compose на Linux).
2. **Установить GNU Make.**
3. **Создать .env файл c API и переместить его в deploy** (ниже описано как это сделать)
4. **Запустить нужную цель** (`make win_all` на Windows, `make linux_all` на macOS/Linux).
5. **Перейти на http://localhost:3000** (можно прямо из Docker)

**ПЕРВАЯ СБОРКА БУДЕТ ДОЛГОЙ, ТАК-КАК НУЖНО СОБРАТЬ ТЯЖЕЛЫЕ ГЕОГРАФИЧЕСКИЕ ДЕРЕВЬЯ**

### Windows

1. Установите [Docker Desktop](https://www.docker.com/products/docker-desktop/) и убедитесь, что он запущен.

2. Установите GNU Make, например одним из способов:
    - `choco install make` (через [Chocolatey](https://chocolatey.org/)),
    - либо через Git Bash / MSYS2 (`pacman -S make`),

- либо через `winget install GnuWin32.Make`. (recommended)

3. В корне проекта выполните:

```shell
   make win_all
*не забудьте создать .env с api - ключом
## Linux

### 1. Установка Docker

Установите Docker Engine и плагин Compose.

**Ubuntu / Debian:**

```bas
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
```

2. Установка GNU Make

**Ubuntu / Debian:**

```bash
sudo apt install -y make
```

4. Запуск проекта

В корне проекта выполните:

```bash
make linux_all
```

*не забудьте создать .env с api - ключом

## Переменные окружения

Сервис использует Yandex Geocoder API для превращения адресов в значения долготы и широты.
Для использования API необходимо [создать ключ](https://yandex.ru/maps-api/docs/geocoder-api/quickstart.html)
(доступен бесплатный тариф, которого достаточно для тестирования).

Получите ключ и создайте `deploy/.env` файл в папке `deploy`, в него добавьте переменную `YANDEX_GEOCODER_API_KEY`.
(YANDEX_GEOCODER_API_KEY=ваш_ключ_здесь)

## Зависимости и виртуальное окружение

Проект использует [uv](https://docs.astral.sh/uv/) для управления зависимостями и виртуальным окружением. Если хотите
сделать всё вручную то:

1. Установите `uv` ([инструкция по установке](https://docs.astral.sh/uv/getting-started/installation/)).

2. Установите зависимости и создайте виртуальное окружение:

```shell
   uv sync
```

Это создаст `.venv` (Python 3.12) и установит зависимости из `uv.lock`.

3. Активируйте окружение (`source .venv/bin/activate` на Linux/macOS, `.venv\Scripts\activate` на Windows) либо
   запускайте команды через `uv run ...` без активации.

## Данные

Чтобы создать тестовые данные из данных в хакатоне:

1. Создайте папку `data` и распакуйте в неё все данные, которые были даны в чате, все csv имеют кодировку windows-1251
2. Запустите `transform_data.ipynb`

## Генерация тестовых данных

Для генерации тестовых данных:

1. В папке `data` создать директорию `addresses`
2. Положить в нее таблицу `moscow_vao.csv`

Формат таблицы:

| adresses                                                      |
|---------------------------------------------------------------|
| город Москва,Косинская улица,дом 26А                          |
| город Москва,3-я Владимирская улица,дом 9,корпус 3,строение 3 |

[Яндекс диск с moscow_vao.csv](https://disk.360.yandex.ru/i/AzAhUVJQSPe6qw)

## OSRM и запуск через Makefile

Вместо ручных команд ниже можно (и нужно) использовать `Makefile` — он скачивает карту, вырезает Московскую область,
собирает профили OSRM (car/bicycle/foot) и поднимает docker compose одной командой.

### Linux / WSL / Git Bash

```shell
make linux_all
```

Это выполнит по порядку:

1. `linux_download` — скачает карту ЦФО в `osrm_arts/map.osm.pbf` (если её ещё нет)
2. `linux_clip` — вырежет из неё Московскую область (`osrm_arts/moscow-oblast.osm.pbf`)
3. `linux_osrm_all` — соберёт все три профиля (`car`, `bicycle`, `foot`) в `osrm/<profile>/`
4. `linux_up` — поднимет `docker compose` из `deploy/`

Отдельные шаги при необходимости:

```shell
make linux_download          # скачать карту
make linux_clip               # вырезать регион
make linux_osrm_car           # собрать только car
make linux_osrm_bicycle       # собрать только bicycle
make linux_osrm_foot          # собрать только foot
make linux_up                 # поднять сервисы
```

### Windows

Аналогичный набор целей с префиксом `win_`:

```shell
make win_all
```

или по шагам:

```shell
make win_download
make win_clip
make win_osrm_car
make win_osrm_bicycle
make win_osrm_foot
make win_up
```

**Важно для Windows:**

- Используйте GNU Make (например, через Git Bash/MSYS2 или `choco install make`) — команды написаны под `cmd /C`,
  поэтому их можно запускать и из PowerShell/Git Bash, если сам `make` установлен.
- Каждая цель уже проверяет, скачан/собран ли профиль (`.built`-маркер), поэтому повторный `make win_all` не будет
  пересобирать то, что уже готово — можно просто запускать `make win_all` снова после обрыва.
- Если Docker Desktop не видит примонтированные тома — проверьте, что общий доступ к диску (Drive sharing / File
  sharing) включён в настройках Docker Desktop.

### Пересборка одного профиля

Если нужно пересобрать конкретный профиль заново (например, после обновления карты), удалите его маркер и папку:

```shell
rm -rf osrm/car   # Linux/WSL
# или
rmdir /s /q osrm\car   # Windows cmd
```

и запустите соответствующую цель (`make linux_osrm_car` / `make win_osrm_car`) заново.

### Очистка

```shell
make clean
```

Удаляет `osrm_arts/` и `osrm/` целиком — используйте, если нужно начать сборку карты с нуля.
