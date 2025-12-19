from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import json

@login_required
def reports_dashboard(request):
    """Панель отчетов"""
    return render(request, 'reports/dashboard.html')

@login_required
def financial_report(request):
    """Финансовый отчет"""
    from payments.models import Payment
    from django.db.models.functions import TruncMonth
    
    # Статистика по месяцам
    monthly_stats = Payment.objects.filter(status='completed').annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')
    
    # Подготовка данных для графика
    chart_data = {
        'labels': [stat['month'].strftime('%b %Y') for stat in monthly_stats],
        'data': [float(stat['total']) for stat in monthly_stats]
    }
    
    context = {
        'monthly_stats': monthly_stats,
        'chart_data_json': json.dumps(chart_data),
    }
    return render(request, 'reports/financial.html', context)

@login_required
def clients_report(request):
    """Отчет по клиентам"""
    from clients.models import Client
    from subscriptions.models import Membership
    
    # Статистика по клиентам
    clients_by_status = Client.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Новые клиенты по месяцам
    from django.db.models.functions import TruncMonth
    new_clients_monthly = Client.objects.annotate(
        month=TruncMonth('registration_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')[:12]
    
    # Клиенты с активными абонементами
    clients_with_active = Client.objects.filter(
        memberships__status='active'
    ).distinct().count()
    
    context = {
        'clients_by_status': clients_by_status,
        'new_clients_monthly': new_clients_monthly,
        'clients_with_active': clients_with_active,
        'total_clients': Client.objects.count(),
    }
    return render(request, 'reports/clients.html', context)

@login_required
def membership_report(request):
    """Отчет по абонементам"""
    from subscriptions.models import Membership, MembershipPlan
    
    # Статистика по статусам
    memberships_by_status = Membership.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Популярные тарифы
    popular_plans = MembershipPlan.objects.annotate(
        active_count=Count('memberships', filter=Q(memberships__status='active')),
        total_count=Count('memberships')
    ).order_by('-active_count')[:10]
    
    # Истекающие абонементы
    today = timezone.now().date()
    week_later = today + timedelta(days=7)
    expiring_soon = Membership.objects.filter(
        status='active',
        end_date__range=[today, week_later]
    ).count()
    
    context = {
        'memberships_by_status': memberships_by_status,
        'popular_plans': popular_plans,
        'expiring_soon': expiring_soon,
        'total_memberships': Membership.objects.count(),
        'active_memberships': Membership.objects.filter(status='active').count(),
    }
    return render(request, 'reports/memberships.html', context)

@login_required
def export_clients_pdf(request):
    """Экспорт клиентов в PDF"""
    from clients.models import Client
    
    # Создаем PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Заголовок
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "Список клиентов фитнес-клуба")
    
    # Данные
    p.setFont("Helvetica", 10)
    y = 750
    clients = Client.objects.all()
    
    for client in clients:
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = 750
        
        p.drawString(50, y, f"{client.get_full_name()}")
        p.drawString(200, y, f"{client.phone}")
        p.drawString(300, y, f"{client.email or '-'}")
        y -= 20
    
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="clients.pdf"'
    return response

@login_required
def export_payments_excel(request):
    """Экспорт платежей в Excel"""
    from payments.models import Payment
    
    # Создаем Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Платежи"
    
    # Заголовки
    headers = ['ID', 'Дата', 'Клиент', 'Сумма', 'Тип', 'Метод', 'Статус']
    for col_num, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_num, value=header)
    
    # Данные
    payments = Payment.objects.all().select_related('client')
    for row_num, payment in enumerate(payments, 2):
        ws.cell(row=row_num, column=1, value=payment.id)
        ws.cell(row=row_num, column=2, value=payment.payment_date.strftime("%d.%m.%Y %H:%M"))
        ws.cell(row=row_num, column=3, value=payment.client.get_full_name())
        ws.cell(row=row_num, column=4, value=float(payment.amount))
        ws.cell(row=row_num, column=5, value=payment.get_payment_type_display_name())
        ws.cell(row=row_num, column=6, value=payment.get_payment_method_display_name())
        ws.cell(row=row_num, column=7, value=payment.get_status_display_name())
    
    # Сохраняем
    buffer = io.BytesIO()
    wb.save(buffer)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="payments.xlsx"'
    return response