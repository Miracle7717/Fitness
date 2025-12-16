from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class MembershipPlan(models.Model):
    # Типы периодов
    PERIOD_CHOICES = [
        ('days', 'Дни'),
        ('months', 'Месяцы'),
        ('year', 'Год'),
    ]
    
    # Время доступа
    ACCESS_TIME_CHOICES = [
        ('any', 'Любое время'),
        ('day', 'Дневное (6:00-18:00)'),
        ('night', 'Ночное (18:00-6:00)'),
        ('weekend', 'Только выходные'),
    ]
    
    # Название тарифа
    name = models.CharField(
        max_length=100,
        verbose_name='Название тарифа',
        unique=True,
        help_text='Например: "Месячный безлимит", "Разовое посещение"'
    )
    
    # Описание
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
        help_text='Подробное описание тарифа'
    )
    
    # Цена
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        validators=[MinValueValidator(0)]
    )
    
    # Период действия
    period_value = models.IntegerField(
        verbose_name='Значение периода',
        default=30,
        help_text='Например: 30 дней, 12 месяцев, 1 год'
    )
    
    period_type = models.CharField(
        max_length=10,
        verbose_name='Тип периода',
        choices=PERIOD_CHOICES,
        default='days'
    )
    
    # Ограничения посещений (если есть)
    visit_limit = models.IntegerField(
        verbose_name='Лимит посещений',
        blank=True,
        null=True,
        help_text='Оставьте пустым для безлимитного тарифа'
    )
    
    # Время доступа
    access_time = models.CharField(
        max_length=20,
        verbose_name='Время доступа',
        choices=ACCESS_TIME_CHOICES,
        default='any'
    )
    
    # Возможность заморозки
    can_freeze = models.BooleanField(
        verbose_name='Можно заморозить',
        default=False,
        help_text='Разрешить клиенту замораживать абонемент'
    )
    
    # Максимальное время заморозки (в днях)
    max_freeze_days = models.IntegerField(
        verbose_name='Максимальная заморозка (дней)',
        default=0,
        help_text='0 - без ограничений'
    )
    
    # Активность тарифа
    is_active = models.BooleanField(
        verbose_name='Активный тариф',
        default=True,
        help_text='Отображается ли тариф для покупки'
    )
    
    # Порядок отображения
    display_order = models.IntegerField(
        verbose_name='Порядок отображения',
        default=0,
        help_text='Чем меньше число, тем выше в списке'
    )
    
    # Автоматические поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Тарифный план'
        verbose_name_plural = 'Тарифные планы'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return f'{self.name} - {self.price} руб.'
    
    def get_period_display_text(self):
        """Текстовое представление периода"""
        period_texts = {
            'days': 'дней',
            'months': 'месяцев',
            'year': 'год'
        }
        return f'{self.period_value} {period_texts.get(self.period_type, "")}'
    
    def is_unlimited(self):
        """Безлимитный ли тариф"""
        return self.visit_limit is None
    
    def get_access_time_display_text(self):
        """Текстовое представление времени доступа"""
        access_texts = {
            'any': 'Любое время',
            'day': 'Дневное время (6:00-18:00)',
            'night': 'Ночное время (18:00-6:00)',
            'weekend': 'Только выходные',
        }
        return access_texts.get(self.access_time, 'Любое время')
    
    @property
    def price_per_day(self):
        """Стоимость за день (для сравнения тарифов)"""
        if self.period_type == 'days':
            days = self.period_value
        elif self.period_type == 'months':
            days = self.period_value * 30  # приблизительно
        elif self.period_type == 'year':
            days = self.period_value * 365
        else:
            days = 1
        
        if days > 0:
            return round(self.price / days, 2)
        return self.price
    
    @classmethod
    def get_active_plans(cls):
        """Получить все активные тарифы"""
        return cls.objects.filter(is_active=True).order_by('display_order', 'name')


class Membership(models.Model):
    # Статусы абонемента
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('expired', 'Истек'),
        ('frozen', 'Заморожен'),
        ('cancelled', 'Отменен'),
    ]
    
    # Связи
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        verbose_name='Клиент',
        related_name='memberships'
    )
    
    plan = models.ForeignKey(
        'MembershipPlan',
        on_delete=models.PROTECT,
        verbose_name='Тарифный план',
        related_name='memberships'
    )
    
    # Даты
    start_date = models.DateField(
        verbose_name='Дата начала',
        default=timezone.now
    )
    
    end_date = models.DateField(
        verbose_name='Дата окончания',
        blank=True,
        null=True
    )
    
    # Оставшиеся посещения (если тариф ограниченный)
    remaining_visits = models.IntegerField(
        verbose_name='Оставшиеся посещения',
        blank=True,
        null=True
    )
    
    # Статус
    status = models.CharField(
        max_length=20,
        verbose_name='Статус',
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Автопродление
    auto_renewal = models.BooleanField(
        verbose_name='Автопродление',
        default=False
    )
    
    # Дата заморозки (если абонемент заморожен)
    frozen_until = models.DateField(
        verbose_name='Заморожен до',
        blank=True,
        null=True
    )
    
    # Примечания
    notes = models.TextField(
        verbose_name='Примечания',
        blank=True,
        null=True
    )
    
    # Автоматические поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['end_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f'{self.client} - {self.plan.name} ({self.status})'
    
    def save(self, *args, **kwargs):
        """Автоматически устанавливаем дату окончания при сохранении"""
        if not self.end_date and self.plan:
            # Рассчитываем дату окончания на основе тарифа
            from datetime import timedelta
            
            if self.plan.period_type == 'days':
                delta = timedelta(days=self.plan.period_value)
            elif self.plan.period_type == 'months':
                # Приблизительно 30 дней в месяце
                delta = timedelta(days=self.plan.period_value * 30)
            elif self.plan.period_type == 'year':
                delta = timedelta(days=self.plan.period_value * 365)
            else:
                delta = timedelta(days=30)
            
            self.end_date = self.start_date + delta
        
        # Устанавливаем количество посещений, если тариф ограниченный
        if not self.remaining_visits and self.plan.visit_limit:
            self.remaining_visits = self.plan.visit_limit
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Проверка, истек ли абонемент"""
        if self.status == 'expired':
            return True
        if self.end_date and self.end_date < timezone.now().date():
            return True
        return False
    
    def days_remaining(self):
        """Сколько дней осталось до истечения"""
        if not self.end_date:
            return None
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    def can_enter(self):
        """Может ли клиент войти по этому абонементу"""
        if self.status != 'active':
            return False
        if self.is_expired():
            return False
        if self.remaining_visits is not None and self.remaining_visits <= 0:
            return False
        return True
    
    def use_visit(self):
        """Использовать одно посещение"""
        if self.remaining_visits is not None and self.remaining_visits > 0:
            self.remaining_visits -= 1
            if self.remaining_visits <= 0:
                self.status = 'expired'
            self.save()
            return True
        return False
    
    def freeze(self, until_date):
        """Заморозить абонемент"""
        if not self.plan.can_freeze:
            return False, "Тариф не поддерживает заморозку"
        
        self.status = 'frozen'
        self.frozen_until = until_date
        self.save()
        return True, "Абонемент заморожен"
    
    def unfreeze(self):
        """Разморозить абонемент"""
        if self.status != 'frozen':
            return False, "Абонемент не заморожен"
        
        self.status = 'active'
        self.frozen_until = None
        self.save()
        return True, "Абонемент разморожен"
    
    @property
    def is_about_to_expire(self):
        """Абонемент скоро истекает (менее 7 дней)"""
        days_left = self.days_remaining()
        return days_left is not None and 0 < days_left <= 7