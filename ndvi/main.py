import geopandas as gpd
import ee
import numpy as np

# Аутентификация в Google Earth Engine
ee.Initialize()

# Загрузите KML файл
kml = gpd.read_file('fields.kml')
coords = kml.geometry.total_bounds  # Получите границы области

# Определите область интереса
aoi = ee.Geometry.Rectangle([coords[0], coords[1], coords[2], coords[3]])

# Загрузите данные Sentinel-2
image = ee.ImageCollection('COPERNICUS/S2') \
          .filterBounds(aoi) \
          .filterDate('2023-01-01', '2023-12-31') \
          .median()

# Рассчитайте NDVI
ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

# Экспортируйте NDVI в GeoTIFF
url = ndvi.getDownloadURL({
    'scale': 10,
    'region': aoi,
    'format': 'GeoTIFF'
})

print(f"Скачайте NDVI изображение по следующей ссылке: {url}")
