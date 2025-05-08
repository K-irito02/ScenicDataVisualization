from django.contrib import admin
from .models import (
    ScenicData, PriceData, ProvinceTraffic, TrafficData, TimeData,
    ScenicLevelPrice, MuseumLevelPrice, GeoLogicalParkLevelPrice,
    ForestParkLevelPrice, WetlandLevelPrice, CulturalRelicLevelPrice,
    NatureReserveLevelPrice
)

# 注册所有模型到Django管理后台
admin.site.register(ScenicData)
admin.site.register(PriceData)
admin.site.register(ProvinceTraffic)
admin.site.register(TrafficData)
admin.site.register(TimeData)
admin.site.register(ScenicLevelPrice)
admin.site.register(MuseumLevelPrice)
admin.site.register(GeoLogicalParkLevelPrice)
admin.site.register(ForestParkLevelPrice)
admin.site.register(WetlandLevelPrice)
admin.site.register(CulturalRelicLevelPrice)
admin.site.register(NatureReserveLevelPrice)