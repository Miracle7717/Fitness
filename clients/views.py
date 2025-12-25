from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Client
from .forms import ClientForm, ClientSearchForm
from subscriptions.models import Membership

@login_required
def client_list(request):
    """Список всех клиентов"""
    form = ClientSearchForm(request.GET or None)
    clients = Client.objects.all().order_by('last_name', 'first_name')
    
    # Применяем фильтры поиска
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        
        if search:
            clients = clients.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(middle_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )
        
        if status:
            clients = clients.filter(status=status)
    
    # Пагинация
    paginator = Paginator(clients, 10)  # 10 клиентов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_clients': clients.count(),
    }
    return render(request, 'clients/client_list.html', context)

@login_required
def client_detail(request, pk):
    """Детальная информация о клиенте"""
    client = get_object_or_404(Client, pk=pk)
    
    # Получаем активные абонементы клиента
    active_memberships = client.memberships.filter(status='active')
    expired_memberships = client.memberships.filter(status='expired')
    all_memberships = client.memberships.all().order_by('-start_date')
    
    context = {
        'client': client,
        'active_memberships': active_memberships,
        'expired_memberships': expired_memberships,
        'all_memberships': all_memberships,
    }
    return render(request, 'clients/client_detail.html', context)

@login_required
def client_create(request):
    """Создание нового клиента"""
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Клиент {client.get_full_name()} успешно создан!')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm()
    
    context = {'form': form}
    return render(request, 'clients/client_form.html', context)

@login_required
def client_update(request, pk):
    """Редактирование клиента"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Данные клиента {client.get_full_name()} обновлены!')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client': client,
    }
    return render(request, 'clients/client_form.html', context)

@login_required
def client_delete(request, pk):
    """Удаление клиента"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        client_name = client.get_full_name()
        client.delete()
        messages.success(request, f'Клиент {client_name} удален!')
        return redirect('client_list')
    
    context = {'client': client}
    return render(request, 'clients/client_confirm_delete.html', context)

@login_required
def client_statistics(request):
    """Статистика по клиентам"""
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(status='active').count()
    inactive_clients = Client.objects.filter(status='inactive').count()
    suspended_clients = Client.objects.filter(status='suspended').count()
    
    # Клиенты с активными абонементами
    clients_with_active_memberships = Client.objects.filter(
        memberships__status='active'
    ).distinct().count()
    
    # Новые клиенты за последние 30 дней
    from django.utils import timezone
    from datetime import timedelta
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_clients = Client.objects.filter(
        registration_date__gte=thirty_days_ago
    ).count()
    
    context = {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'inactive_clients': inactive_clients,
        'suspended_clients': suspended_clients,
        'clients_with_active_memberships': clients_with_active_memberships,
        'new_clients': new_clients,
    }
    return render(request, 'clients/client_statistics.html', context)

@login_required
def export_clients_pdf(request):
    """Экспорт клиентов в PDF"""
    from django.http import HttpResponse
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    
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