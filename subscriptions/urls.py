from django.urls import path
from . import views

urlpatterns = [
    # Тарифные планы
    path('plans/', views.membership_plan_list, name='membership_plan_list'),
    path('plans/create/', views.membership_plan_create, name='membership_plan_create'),
    path('plans/<int:pk>/', views.membership_plan_detail, name='membership_plan_detail'),
    path('plans/<int:pk>/update/', views.membership_plan_update, name='membership_plan_update'),
    path('plans/<int:pk>/delete/', views.membership_plan_delete, name='membership_plan_delete'),
    
    # Абонементы
    path('', views.membership_list, name='membership_list'),
    path('create/', views.membership_create, name='membership_create'),
    path('<int:pk>/', views.membership_detail, name='membership_detail'),
    path('<int:pk>/update/', views.membership_update, name='membership_update'),
    path('<int:pk>/delete/', views.membership_delete, name='membership_delete'),
    path('<int:pk>/visit/', views.register_visit, name='register_visit'),
    
    # Специальные страницы
    path('expiring/', views.membership_expiring, name='membership_expiring'),
    path('expired/', views.membership_expired, name='membership_expired'),
    path('statistics/', views.membership_statistics, name='membership_statistics'),
]