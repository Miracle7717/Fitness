from django.urls import path
from . import views

urlpatterns = [
    # Платежи
    path('', views.payment_list, name='payment_list'),
    path('create/', views.payment_create, name='payment_create'),
    path('create/subscription/<int:membership_id>/', views.create_subscription_payment, name='create_subscription_payment'),
    path('<int:pk>/', views.payment_detail, name='payment_detail'),
    path('<int:pk>/update/', views.payment_update, name='payment_update'),
    path('<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('statistics/', views.payment_statistics, name='payment_statistics'),
    path('export/excel/', views.export_payments_excel, name='export_payments_excel'),
    
    # Напоминания
    path('reminders/', views.reminder_list, name='reminder_list'),
    path('reminders/create/', views.reminder_create, name='reminder_create'),
    path('reminders/<int:pk>/send/', views.reminder_send_now, name='reminder_send_now'),
    
    # Должники
    path('debtors/', views.debtors_list, name='debtors_list'),
]