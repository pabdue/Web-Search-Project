from django.contrib import admin
from django.urls import path
from . import views


app_name = 'demo_app' 

urlpatterns = [
    path('demo/search/', views.search_view, name='search_view'),
    path('demo/about/', views.about_view, name='about_view'),
    path('search/', views.search_civil_research, name='search_civil_research'),
]