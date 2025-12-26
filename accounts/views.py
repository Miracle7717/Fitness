from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm, UserUpdateForm
from .models import User
from clients.models import Client
from subscriptions.models import Membership, MembershipPlan
from payments.models import Payment
from django.utils import timezone
import datetime
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
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

def register_view(request):
    """View для регистрации нового пользователя"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Аккаунт создан успешно! Добро пожаловать, {user.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    """View для просмотра и редактирования профиля"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    """Дашборд системы с расширенной аналитикой"""
    today = timezone.now().date()
    
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(status='active').count()
    new_clients_today = Client.objects.filter(
        registration_date__date=today
    ).count()
    new_clients_month = Client.objects.filter(
        registration_date__date__gte=today.replace(day=1)
    ).count()
    
    active_memberships = Membership.objects.filter(status='active').count()
    total_memberships = Membership.objects.count()
    
    week_later = today + datetime.timedelta(days=7)
    expiring_soon = Membership.objects.filter(
        status='active',
        end_date__range=[today, week_later]
    ).count()
    
    expired = Membership.objects.filter(
        status='active',
        end_date__lt=today
    ).count()
    
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
    
    popular_plans = MembershipPlan.objects.annotate(
        active_count=Count('memberships', filter=Q(memberships__status='active'))
    ).filter(active_count__gt=0).order_by('-active_count')[:5]
    
    recent_payments = Payment.objects.filter(
        status='completed'
    ).select_related('client').order_by('-payment_date')[:10]
    
    recent_clients = Client.objects.all().order_by('-registration_date')[:10]
    
    completed_payments_count = Payment.objects.filter(status='completed').count()
    statistics = {
        'avg_payment': total_payments / completed_payments_count if completed_payments_count > 0 else 0,
        'clients_with_memberships': Client.objects.filter(memberships__status='active').distinct().count(),
        'renewal_rate': '78%',  
        'occupancy_rate': '65%',  
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

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'