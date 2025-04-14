from django.urls import path
from . import views

urlpatterns = [
    # 省份景区分布数据
    path('data/province-distribution/', views.ProvinceDistributionView.as_view(), name='province-distribution'),
    
    # 景区等级与分类数据
    path('data/scenic-levels/', views.ScenicLevelsView.as_view(), name='scenic-levels'),
    
    # 门票价格数据
    path('data/ticket-prices/', views.TicketPricesView.as_view(), name='ticket-prices'),
    
    # 开放时间数据
    path('data/open-times/', views.OpenTimesView.as_view(), name='open-times'),
    
    # 评论情感分析数据
    path('data/comment-analysis/', views.CommentAnalysisView.as_view(), name='comment-analysis'),
    
    # 景区词云数据
    path('data/word-cloud/<str:scenic_id>/', views.WordCloudView.as_view(), name='word-cloud'),
    
    # 交通方式数据
    path('data/transportation/', views.TransportationView.as_view(), name='transportation'),
    
    # 景区搜索接口
    path('scenic/search/', views.ScenicSearchView.as_view(), name='scenic-search'),
    
    # 筛选选项数据
    path('data/filter-options/', views.FilterOptionsView.as_view(), name='filter-options'),
    
    # 景区详情接口
    path('scenic/<str:pk>/', views.ScenicDetailView.as_view(), name='scenic-detail'),
    
    # 省份城市景区分布数据
    path('data/province-city-distribution/<str:province_name>/', views.ProvinceCityDistributionView.as_view(), name='province-city-distribution'),
    
    # 区县景区分布数据
    path('data/district-distribution/<str:province_name>/<str:city_name>/', views.DistrictDistributionView.as_view(), name='district-distribution'),
    
    # 情感倾向分布数据
    path('data/sentiment-distribution/', views.SentimentDistributionView.as_view(), name='sentiment-distribution'),
    
    # 情感得分与景区类型等级关系数据
    path('data/sentiment-type/', views.SentimentTypeView.as_view(), name='sentiment-type'),
    
    # 景区类型平均门票价格
    path('data/ticket-avg-price/', views.TicketAvgPriceView.as_view(), name='ticket-avg-price'),
    
    # 各景区类型门票价格箱线图数据
    path('data/ticket-boxplot-by-type/', views.TicketBoxplotByTypeView.as_view(), name='ticket-boxplot-by-type'),
    
    # 指定景区类型各等级门票价格箱线图数据
    path('data/ticket-boxplot-by-level/', views.TicketBoxplotByLevelView.as_view(), name='ticket-boxplot-by-level'),
] 