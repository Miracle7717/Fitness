from django import forms
from django.core.validators import MinValueValidator
from .models import MembershipPlan, Membership

class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = [
            'name', 'description', 'price',
            'period_value', 'period_type',
            'visit_limit', 'access_time',
            'can_freeze', 'max_freeze_days',
            'is_active', 'display_order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Месячный безлимит'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Подробное описание тарифа...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'period_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'period_type': forms.Select(attrs={'class': 'form-control'}),
            'visit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Оставьте пустым для безлимитного'
            }),
            'access_time': forms.Select(attrs={'class': 'form-control'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'can_freeze': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError('Цена должна быть больше 0')
        return price
    
    def clean_visit_limit(self):
        visit_limit = self.cleaned_data.get('visit_limit')
        if visit_limit is not None and visit_limit <= 0:
            raise forms.ValidationError('Лимит посещений должен быть больше 0')
        return visit_limit

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = [
            'client', 'plan', 'start_date',
            'auto_renewal', 'notes'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'plan': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'auto_renewal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные заметки...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только активных клиентов
        from clients.models import Client
        self.fields['client'].queryset = Client.objects.filter(status='active')
        # Показываем только активные тарифы
        self.fields['plan'].queryset = MembershipPlan.objects.filter(is_active=True)

class MembershipUpdateForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = [
            'status', 'remaining_visits',
            'auto_renewal', 'frozen_until', 'notes'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remaining_visits': forms.NumberInput(attrs={'class': 'form-control'}),
            'auto_renewal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frozen_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class MembershipSearchForm(forms.Form):
    """Форма поиска абонементов"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по клиенту...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Все статусы')] + Membership.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    plan = forms.ModelChoiceField(
        required=False,
        queryset=MembershipPlan.objects.all(),
        empty_label='Все тарифы',
        widget=forms.Select(attrs={'class': 'form-control'})
    )