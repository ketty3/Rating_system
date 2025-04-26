from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('', views.dashboard, name='dashboard'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
]



