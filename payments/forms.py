from django import forms
from django.core.validators import MinValueValidator
from .models import Payment, Reminder

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'client', 'membership', 'membership_plan',
            'amount', 'payment_date', 'payment_type',
            'payment_method', 'status', 'period_start',
            'period_end', 'receipt', 'notes'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'membership': forms.Select(attrs={'class': 'form-control'}),
            'membership_plan': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'payment_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'period_start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'period_end': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только активных клиентов
        from clients.models import Client
        self.fields['client'].queryset = Client.objects.filter(status='active')
        
        # Показываем только активные абонементы
        from subscriptions.models import Membership
        self.fields['membership'].queryset = Membership.objects.filter(status='active')
        
        # Показываем только активные тарифы
        from subscriptions.models import MembershipPlan
        self.fields['membership_plan'].queryset = MembershipPlan.objects.filter(is_active=True)

class PaymentSearchForm(forms.Form):
    """Форма поиска платежей"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по клиенту...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Все статусы')] + Payment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    payment_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Все типы')] + Payment.PAYMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = [
            'client', 'membership', 'reminder_type',
            'send_date', 'send_method', 'subject', 'message'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'membership': forms.Select(attrs={'class': 'form-control'}),
            'reminder_type': forms.Select(attrs={'class': 'form-control'}),
            'send_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'send_method': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),
        }