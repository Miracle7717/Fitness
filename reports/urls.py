from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('financial/', views.financial_report, name='financial_report'),
    path('clients/', views.clients_report, name='clients_report'),
    path('memberships/', views.membership_report, name='membership_report'),
    
    # Экспорт
    path('export/clients/pdf/', views.export_clients_pdf, name='export_clients_pdf'),
    path('export/payments/excel/', views.export_payments_excel, name='export_payments_excel'),
]