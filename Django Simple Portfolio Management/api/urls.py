# -*- encoding: utf-8 -*-


from django.urls import path
from api import views
from rest_framework.urlpatterns import format_suffix_patterns

from django.urls import path



urlpatterns = [
    # path('search-results/', views.Search_ResultsListCreateView.as_view(), name='search-result-list'),
    # path('search-queries/', views.Search_QueryListCreateView.as_view(), name='search-query-list'),


    path('add/stock/', views.add_stock_data, name='add.stock'),


]
urlpatterns = format_suffix_patterns(urlpatterns)
