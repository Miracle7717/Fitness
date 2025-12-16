from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('statistics/', views.client_statistics, name='client_statistics'),
    path('create/', views.client_create, name='client_create'),
    path('<int:pk>/', views.client_detail, name='client_detail'),
    path('<int:pk>/update/', views.client_update, name='client_update'),
    path('<int:pk>/delete/', views.client_delete, name='client_delete'),
]