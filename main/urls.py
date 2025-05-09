from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('home/', views.home_page, name='home'),
    path('', views.dashboard, name='dashboard'),
    path('news/', views.news, name='news'),
    path('study/', views.study, name='study'),
    path('events/', views.events, name='events'),
    path('shop/', views.shop, name='shop'),
    path('orders/', views.orders, name='orders'),
    path('subjects/', views.subjects, name='subjects'),
    path('registrations/', views.registrations, name='registrations'),
    path('operations/', views.operations, name='operations'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
