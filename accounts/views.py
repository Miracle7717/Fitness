from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm
from clients.models import Client
from subscriptions.models import Membership, MembershipPlan
from payments.models import Payment
from django.utils import timezone
import datetime
from django.db.models import Count, Sum, Q

def login_view(request):
    """Кастомный view для входа в систему"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """View для выхода из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')

@login_required
def dashboard_view(request):
    """Дашборд системы с расширенной аналитикой"""
    today = timezone.now().date()
    
    # 1. Статистика клиентов
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(status='active').count()
    new_clients_today = Client.objects.filter(
        registration_date__date=today
    ).count()
    new_clients_month = Client.objects.filter(
        registration_date__date__gte=today.replace(day=1)
    ).count()
    
    # 2. Статистика абонементов
    active_memberships = Membership.objects.filter(status='active').count()
    total_memberships = Membership.objects.count()
    
    # Абонементы, которые скоро истекут (менее 7 дней)
    week_later = today + datetime.timedelta(days=7)
    expiring_soon = Membership.objects.filter(
        status='active',
        end_date__range=[today, week_later]
    ).count()
    
    # Просроченные абонементы
    expired = Membership.objects.filter(
        status='active',
        end_date__lt=today
    ).count()
    
    # 3. Статистика платежей
    total_payments = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    today_payments = Payment.objects.filter(
        status='completed',
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_payments = Payment.objects.filter(
        status='completed',
        payment_date__date__gte=today.replace(day=1)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # 4. Популярные тарифы
    popular_plans = MembershipPlan.objects.annotate(
        active_count=Count('memberships', filter=Q(memberships__status='active'))
    ).filter(active_count__gt=0).order_by('-active_count')[:5]
    
    # 5. Последние платежи
    recent_payments = Payment.objects.filter(
        status='completed'
    ).select_related('client').order_by('-payment_date')[:10]
    
    # 6. Последние клиенты
    recent_clients = Client.objects.all().order_by('-registration_date')[:10]
    
    # 7. Общая статистика
    completed_payments_count = Payment.objects.filter(status='completed').count()
    statistics = {
        'avg_payment': total_payments / completed_payments_count if completed_payments_count > 0 else 0,
        'clients_with_memberships': Client.objects.filter(memberships__status='active').distinct().count(),
        'renewal_rate': '78%',  # В реальном проекте рассчитать
        'occupancy_rate': '65%',  # В реальном проекте рассчитать
    }
    
    context = {
        # Клиенты
        'total_clients': total_clients,
        'active_clients': active_clients,
        'new_clients_today': new_clients_today,
        'new_clients_month': new_clients_month,
        
        # Абонементы
        'active_memberships': active_memberships,
        'total_memberships': total_memberships,
        'expiring_soon': expiring_soon,
        'expired': expired,
        
        # Платежи
        'total_payments': total_payments,
        'today_payments': today_payments,
        'month_payments': month_payments,
        
        # Дополнительные данные
        'popular_plans': popular_plans,
        'recent_payments': recent_payments,
        'recent_clients': recent_clients,
        'statistics': statistics,
        'today': today,
    }
    
    return render(request, 'dashboard.html', context)