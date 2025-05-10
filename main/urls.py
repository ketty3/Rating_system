from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('home/', views.home_page, name='home'),
    path('', views.dashboard, name='dashboard'),
    path('news/', views.news, name='news'),
    path('profile/', views.profile_view, name='profile'),
    path('study/', views.study, name='study'),
    path('events/', views.events, name='events'),
    path('event/register/<int:event_id>/', views.register_event, name='register_event'),

    path('shop/', views.shop, name='shop'),
    path('orders/', views.orders, name='orders'),
    path('subjects/', views.subjects_taught, name='subjects'),
    path('registrations/', views.registrations, name='registrations'),
    path('operations/', views.operations, name='operations'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('subjects/save_grades/<int:subject_id>/', views.save_grades, name='save_grades'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
