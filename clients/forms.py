from django import forms
from django.core.validators import RegexValidator
from .models import Client

class ClientForm(forms.ModelForm):
    phone_validator = RegexValidator(
        regex=r'^\+7\d{10}$',
        message='Телефон должен быть в формате: +7XXXXXXXXXX'
    )
    
    phone = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7XXXXXXXXXX'
        })
    )
    
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'middle_name',
            'phone', 'email', 'birth_date',
            'medical_notes', 'notes', 'status', 'photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'medical_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Медицинские противопоказания...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные заметки...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Проверяем уникальность телефона
        if Client.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Клиент с таким телефоном уже существует.')
        return phone

class ClientSearchForm(forms.Form):
    """Форма поиска клиентов"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по имени, фамилии, телефону...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Все статусы')] + Client.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )