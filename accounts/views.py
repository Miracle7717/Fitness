from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm
from clients.models import Client
from subscriptions.models import Membership
from django.utils import timezone
import datetime

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
    """Дашборд системы"""
    # Получаем статистику для дашборда
    total_clients = Client.objects.count()
    active_memberships = Membership.objects.filter(status='active').count()
    
    # Абонементы, которые скоро истекут (менее 7 дней)
    today = timezone.now().date()
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
    
    context = {
        'total_clients': total_clients,
        'active_memberships': active_memberships,
        'expiring_soon': expiring_soon,
        'expired': expired,
    }
    
    return render(request, 'dashboard.html', context)