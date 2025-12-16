from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import datetime
from .models import MembershipPlan, Membership
from .forms import (
    MembershipPlanForm, MembershipForm, 
    MembershipUpdateForm, MembershipSearchForm
)

# === ТАРИФНЫЕ ПЛАНЫ ===

@login_required
def membership_plan_list(request):
    """Список всех тарифных планов"""
    plans = MembershipPlan.objects.all().order_by('display_order', 'name')
    
    # Разделяем на активные и неактивные
    active_plans = plans.filter(is_active=True)
    inactive_plans = plans.filter(is_active=False)
    
    context = {
        'active_plans': active_plans,
        'inactive_plans': inactive_plans,
    }
    return render(request, 'subscriptions/membership_plan_list.html', context)

@login_required
def membership_plan_detail(request, pk):
    """Детальная информация о тарифном плане"""
    plan = get_object_or_404(MembershipPlan, pk=pk)
    
    # Получаем активные абонементы по этому тарифу
    active_memberships = plan.memberships.filter(status='active')
    
    context = {
        'plan': plan,
        'active_memberships': active_memberships,
    }
    return render(request, 'subscriptions/membership_plan_detail.html', context)

@login_required
def membership_plan_create(request):
    """Создание нового тарифного плана"""
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Тарифный план "{plan.name}" создан!')
            return redirect('membership_plan_detail', pk=plan.pk)
    else:
        form = MembershipPlanForm()
    
    context = {'form': form}
    return render(request, 'subscriptions/membership_plan_form.html', context)

@login_required
def membership_plan_update(request, pk):
    """Редактирование тарифного плана"""
    plan = get_object_or_404(MembershipPlan, pk=pk)
    
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Тарифный план "{plan.name}" обновлен!')
            return redirect('membership_plan_detail', pk=plan.pk)
    else:
        form = MembershipPlanForm(instance=plan)
    
    context = {
        'form': form,
        'plan': plan,
    }
    return render(request, 'subscriptions/membership_plan_form.html', context)

@login_required
def membership_plan_delete(request, pk):
    """Удаление тарифного плана"""
    plan = get_object_or_404(MembershipPlan, pk=pk)
    
    if request.method == 'POST':
        plan_name = plan.name
        # Проверяем, есть ли активные абонементы по этому тарифу
        if plan.memberships.filter(status='active').exists():
            messages.error(request, 
                f'Нельзя удалить тариф "{plan_name}", так как есть активные абонементы.')
            return redirect('membership_plan_detail', pk=plan.pk)
        
        plan.delete()
        messages.success(request, f'Тарифный план "{plan_name}" удален!')
        return redirect('membership_plan_list')
    
    context = {'plan': plan}
    return render(request, 'subscriptions/membership_plan_confirm_delete.html', context)

# === АБОНЕМЕНТЫ ===

@login_required
def membership_list(request):
    """Список всех абонементов"""
    form = MembershipSearchForm(request.GET or None)
    memberships = Membership.objects.all().select_related('client', 'plan').order_by('-start_date')
    
    # Применяем фильтры поиска
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        plan = form.cleaned_data.get('plan')
        
        if search:
            memberships = memberships.filter(
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search) |
                Q(client__phone__icontains=search)
            )
        
        if status:
            memberships = memberships.filter(status=status)
        
        if plan:
            memberships = memberships.filter(plan=plan)
    
    # Фильтры для боковой панели
    today = timezone.now().date()
    
    # Активные абонементы
    active_memberships = memberships.filter(status='active')
    
    # Скоро истекающие (менее 7 дней)
    week_later = today + datetime.timedelta(days=7)
    expiring_soon = active_memberships.filter(
        end_date__range=[today, week_later]
    )
    
    # Просроченные
    expired = active_memberships.filter(end_date__lt=today)
    
    # Пагинация
    paginator = Paginator(memberships, 15)  # 15 абонементов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_memberships': memberships.count(),
        'active_count': active_memberships.count(),
        'expiring_soon_count': expiring_soon.count(),
        'expired_count': expired.count(),
        'today': today,
    }
    return render(request, 'subscriptions/membership_list.html', context)

@login_required
def membership_detail(request, pk):
    """Детальная информация об абонементе"""
    membership = get_object_or_404(Membership, pk=pk)
    
    context = {
        'membership': membership,
    }
    return render(request, 'subscriptions/membership_detail.html', context)

@login_required
def membership_create(request):
    """Создание нового абонемента"""
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = form.save()
            messages.success(request, 
                f'Абонемент для {membership.client.get_full_name()} создан!')
            return redirect('membership_detail', pk=membership.pk)
    else:
        form = MembershipForm()
    
    context = {'form': form}
    return render(request, 'subscriptions/membership_form.html', context)

@login_required
def membership_update(request, pk):
    """Редактирование абонемента"""
    membership = get_object_or_404(Membership, pk=pk)
    
    if request.method == 'POST':
        form = MembershipUpdateForm(request.POST, instance=membership)
        if form.is_valid():
            membership = form.save()
            messages.success(request, 'Абонемент обновлен!')
            return redirect('membership_detail', pk=membership.pk)
    else:
        form = MembershipUpdateForm(instance=membership)
    
    context = {
        'form': form,
        'membership': membership,
    }
    return render(request, 'subscriptions/membership_form.html', context)

@login_required
def membership_delete(request, pk):
    """Удаление абонемента"""
    membership = get_object_or_404(Membership, pk=pk)
    
    if request.method == 'POST':
        client_name = membership.client.get_full_name()
        membership.delete()
        messages.success(request, f'Абонемент клиента {client_name} удален!')
        return redirect('membership_list')
    
    context = {'membership': membership}
    return render(request, 'subscriptions/membership_confirm_delete.html', context)

@login_required
def membership_expiring(request):
    """Список абонементов, которые скоро истекают"""
    today = timezone.now().date()
    week_later = today + datetime.timedelta(days=7)
    
    expiring_memberships = Membership.objects.filter(
        status='active',
        end_date__range=[today, week_later]
    ).select_related('client', 'plan').order_by('end_date')
    
    context = {
        'expiring_memberships': expiring_memberships,
        'today': today,
        'week_later': week_later,
    }
    return render(request, 'subscriptions/membership_expiring.html', context)

@login_required
def membership_expired(request):
    """Список просроченных абонементов"""
    today = timezone.now().date()
    
    expired_memberships = Membership.objects.filter(
        status='active',
        end_date__lt=today
    ).select_related('client', 'plan').order_by('end_date')
    
    context = {
        'expired_memberships': expired_memberships,
        'today': today,
    }
    return render(request, 'subscriptions/membership_expired.html', context)

@login_required
def register_visit(request, pk):
    """Регистрация посещения по абонементу"""
    membership = get_object_or_404(Membership, pk=pk)
    
    if request.method == 'POST':
        if membership.can_enter():
            if membership.use_visit():
                messages.success(request, 
                    f'Посещение зарегистрировано для {membership.client.get_full_name()}.')
            else:
                messages.warning(request, 
                    f'Невозможно зарегистрировать посещение. Возможно, лимит исчерпан.')
        else:
            messages.error(request, 
                f'Абонемент не активен или истек. Посещение не зарегистрировано.')
        
        return redirect('membership_detail', pk=membership.pk)
    
    context = {'membership': membership}
    return render(request, 'subscriptions/register_visit.html', context)

@login_required
def membership_statistics(request):
    """Статистика по абонементам"""
    today = timezone.now().date()
    
    # Общая статистика
    total_memberships = Membership.objects.count()
    active_memberships = Membership.objects.filter(status='active').count()
    expired_memberships = Membership.objects.filter(status='expired').count()
    frozen_memberships = Membership.objects.filter(status='frozen').count()
    
    # Скоро истекающие
    week_later = today + datetime.timedelta(days=7)
    expiring_soon = Membership.objects.filter(
        status='active',
        end_date__range=[today, week_later]
    ).count()
    
    # Просроченные (но еще активные в системе)
    actually_expired = Membership.objects.filter(
        status='active',
        end_date__lt=today
    ).count()
    
    # Распределение по тарифам
    from django.db.models import Count
    plans_stats = MembershipPlan.objects.annotate(
        active_count=Count('memberships', filter=Q(memberships__status='active'))
    ).values('name', 'active_count').order_by('-active_count')
    
    # Новые абонементы за последние 30 дней
    thirty_days_ago = today - datetime.timedelta(days=30)
    new_memberships = Membership.objects.filter(
        start_date__gte=thirty_days_ago
    ).count()
    
    context = {
        'total_memberships': total_memberships,
        'active_memberships': active_memberships,
        'expired_memberships': expired_memberships,
        'frozen_memberships': frozen_memberships,
        'expiring_soon': expiring_soon,
        'actually_expired': actually_expired,
        'plans_stats': plans_stats,
        'new_memberships': new_memberships,
        'today': today,
    }
    return render(request, 'subscriptions/membership_statistics.html', context)