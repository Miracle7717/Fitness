from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from django.utils import timezone
import os

def client_photo_path(instance, filename):
    # Файл будет загружен в MEDIA_ROOT/clients/photos/client_<id>/<filename>
    ext = filename.split('.')[-1]
    filename = f'photo_{instance.id}.{ext}'
    return os.path.join('clients', 'photos', f'client_{instance.id}', filename)

class Client(models.Model):
    # Статусы клиента
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('suspended', 'Приостановлен'),
    ]
    
    # Поля клиента
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя',
        validators=[MinLengthValidator(2)]
    )
    
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        validators=[MinLengthValidator(2)]
    )
    
    middle_name = models.CharField(
        max_length=50,
        verbose_name='Отчество',
        blank=True,
        null=True
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        unique=True,
        help_text='Формат: +7XXXXXXXXXX'
    )
    
    email = models.EmailField(
        verbose_name='Email',
        blank=True,
        null=True,
        validators=[EmailValidator()]
    )
    
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        blank=True,
        null=True
    )
    
    photo = models.ImageField(
        upload_to=client_photo_path,
        verbose_name='Фото',
        blank=True,
        null=True
    )
    
    medical_notes = models.TextField(
        verbose_name='Медицинские противопоказания',
        blank=True,
        null=True,
        help_text='Укажите ограничения по здоровью, если есть'
    )
    
    registration_date = models.DateTimeField(
        verbose_name='Дата регистрации',
        default=timezone.now
    )
    
    status = models.CharField(
        max_length=20,
        verbose_name='Статус',
        choices=STATUS_CHOICES,
        default='active'
    )
    
    notes = models.TextField(
        verbose_name='Заметки',
        blank=True,
        null=True
    )
    
    # Автоматические поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        if self.middle_name:
            return f'{self.last_name} {self.first_name} {self.middle_name}'
        return f'{self.last_name} {self.first_name}'
    
    def get_full_name(self):
        """Полное ФИО клиента"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
    
    def get_age(self):
        """Возраст клиента"""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        age = today.year - self.birth_date.year
        # Проверяем, был ли уже день рождения в этом году
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age
    
    def is_active(self):
        """Проверка, активен ли клиент"""
        return self.status == 'active'
    
    def get_active_subscriptions(self):
        """Получить активные абонементы клиента"""
        return self.membership_set.filter(status='active')
    
    @property
    def has_medical_restrictions(self):
        """Есть ли медицинские противопоказания"""
        return bool(self.medical_notes)