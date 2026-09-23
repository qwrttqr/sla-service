# How to start

## Зависимости и виртаульное окружение

1. Создайте виртуальное окружение для проекта любым удобным способом (используйте Python 3.12).
2. Установите зависимости `pip install -r requirements.txt`

## Данные

Чтобы создать тестовые данные из данных в хакатоне:

1. Создайте папку `data` и распакуйте в неё все данные
2. Запустите `transform_data.ipynb`

## OSRM

Необходимо скачать данные для работы OSRM-сервисов

```shell
mkdir osrm\car, osrm\bicycle, osrm\foot -Force
cd osrm
curl.exe -L -O https://download.geofabrik.de/russia/central-fed-district-latest.osm.pbf

foreach ($p in "car", "bicycle", "foot") {
  Copy-Item central-fed-district-latest.osm.pbf "$p\map.osm.pbf"
  docker run --rm -v "${PWD}\${p}:/data" osrm/osrm-backend osrm-extract -p "/opt/${p}.lua" /data/map.osm.pbf
  docker run --rm -v "${PWD}\${p}:/data" osrm/osrm-backend osrm-partition /data/map.osrm
  docker run --rm -v "${PWD}\${p}:/data" osrm/osrm-backend osrm-customize /data/map.osrm
}
```