from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import os

def payment_receipt_path(instance, filename):
    # Файл будет загружен в MEDIA_ROOT/payments/receipts/payment_<id>/<filename>
    ext = filename.split('.')[-1]
    filename = f'receipt_{instance.id}.{ext}'
    return os.path.join('payments', 'receipts', f'payment_{instance.id}', filename)

class Payment(models.Model):
    """Модель платежа"""
    
    # Типы платежей
    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Оплата абонемента'),
        ('training', 'Индивидуальная тренировка'),
        ('locker', 'Аренда шкафчика'),
        ('other', 'Прочее'),
    ]
    
    # Методы оплаты
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('transfer', 'Банковский перевод'),
        ('online', 'Онлайн оплата'),
    ]
    
    # Статусы платежа
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('completed', 'Оплачен'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возвращен'),
    ]
    
    # Связи
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        verbose_name='Клиент',
        related_name='payments'
    )
    
    membership = models.ForeignKey(
        'subscriptions.Membership',
        on_delete=models.SET_NULL,
        verbose_name='Абонемент',
        blank=True,
        null=True,
        related_name='payments'
    )
    
    membership_plan = models.ForeignKey(
        'subscriptions.MembershipPlan',
        on_delete=models.SET_NULL,
        verbose_name='Тарифный план',
        blank=True,
        null=True,
        related_name='payments'
    )
    
    # Информация о платеже
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма',
        validators=[MinValueValidator(0)]
    )
    
    payment_date = models.DateTimeField(
        verbose_name='Дата оплаты',
        default=timezone.now
    )
    
    payment_type = models.CharField(
        max_length=20,
        verbose_name='Тип платежа',
        choices=PAYMENT_TYPE_CHOICES,
        default='subscription'
    )
    
    payment_method = models.CharField(
        max_length=20,
        verbose_name='Метод оплаты',
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    
    status = models.CharField(
        max_length=20,
        verbose_name='Статус',
        choices=STATUS_CHOICES,
        default='completed'
    )
    
    # Период действия (для абонементов)
    period_start = models.DateField(
        verbose_name='Начало периода',
        blank=True,
        null=True
    )
    
    period_end = models.DateField(
        verbose_name='Окончание периода',
        blank=True,
        null=True
    )
    
    # Чек/квитанция
    receipt = models.FileField(
        upload_to=payment_receipt_path,
        verbose_name='Чек/квитанция',
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
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['client', 'payment_date']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f'Платеж #{self.id} - {self.client.get_full_name()} - {self.amount} руб.'
    
    def save(self, *args, **kwargs):
        """Автоматически устанавливаем период действия при сохранении"""
        if not self.period_start and self.membership:
            self.period_start = self.membership.start_date
            self.period_end = self.membership.end_date
        
        if not self.period_start:
            self.period_start = timezone.now().date()
        
        if not self.period_end and self.membership_plan:
            # Рассчитываем дату окончания на основе тарифа
            from datetime import timedelta
            
            if self.membership_plan.period_type == 'days':
                delta = timedelta(days=self.membership_plan.period_value)
            elif self.membership_plan.period_type == 'months':
                delta = timedelta(days=self.membership_plan.period_value * 30)
            elif self.membership_plan.period_type == 'year':
                delta = timedelta(days=self.membership_plan.period_value * 365)
            else:
                delta = timedelta(days=30)
            
            self.period_end = self.period_start + delta
        
        super().save(*args, **kwargs)
    
    def get_payment_type_display_name(self):
        """Получить отображаемое название типа платежа"""
        return dict(self.PAYMENT_TYPE_CHOICES).get(self.payment_type, 'Неизвестно')
    
    def get_payment_method_display_name(self):
        """Получить отображаемое название метода оплаты"""
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, 'Неизвестно')
    
    def get_status_display_name(self):
        """Получить отображаемое название статуса"""
        return dict(self.STATUS_CHOICES).get(self.status, 'Неизвестно')
    
    def is_completed(self):
        """Проверка, завершен ли платеж"""
        return self.status == 'completed'
    
    def can_refund(self):
        """Можно ли вернуть платеж"""
        return self.status == 'completed'
    
    @property
    def period_days(self):
        """Количество дней в периоде"""
        if self.period_start and self.period_end:
            return (self.period_end - self.period_start).days
        return 0
    
    @property
    def price_per_day(self):
        """Стоимость за день"""
        if self.period_days > 0:
            return round(self.amount / self.period_days, 2)
        return self.amount

class Reminder(models.Model):
    """Модель напоминания"""
    
    # Типы напоминаний
    REMINDER_TYPE_CHOICES = [
        ('subscription_expiry', 'Истечение абонемента'),
        ('payment_due', 'Напоминание об оплате'),
        ('birthday', 'День рождения'),
        ('visit', 'Напоминание о посещении'),
        ('other', 'Прочее'),
    ]
    
    # Статусы отправки
    SEND_STATUS_CHOICES = [
        ('pending', 'Ожидает отправки'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка отправки'),
        ('cancelled', 'Отменено'),
    ]
    
    # Способы отправки
    SEND_METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push-уведомление'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
    ]
    
    # Связи
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        verbose_name='Клиент',
        related_name='reminders'
    )
    
    membership = models.ForeignKey(
        'subscriptions.Membership',
        on_delete=models.CASCADE,
        verbose_name='Абонемент',
        blank=True,
        null=True,
        related_name='reminders'
    )
    
    payment = models.ForeignKey(
        'Payment',
        on_delete=models.CASCADE,
        verbose_name='Платеж',
        blank=True,
        null=True,
        related_name='reminders'
    )
    
    # Информация о напоминании
    reminder_type = models.CharField(
        max_length=30,
        verbose_name='Тип напоминания',
        choices=REMINDER_TYPE_CHOICES,
        default='subscription_expiry'
    )
    
    send_date = models.DateTimeField(
        verbose_name='Дата отправки'
    )
    
    send_method = models.CharField(
        max_length=20,
        verbose_name='Способ отправки',
        choices=SEND_METHOD_CHOICES,
        default='email'
    )
    
    send_status = models.CharField(
        max_length=20,
        verbose_name='Статус отправки',
        choices=SEND_STATUS_CHOICES,
        default='pending'
    )
    
    # Сообщение
    subject = models.CharField(
        max_length=200,
        verbose_name='Тема',
        blank=True,
        null=True
    )
    
    message = models.TextField(
        verbose_name='Сообщение'
    )
    
    # Результат отправки
    sent_at = models.DateTimeField(
        verbose_name='Отправлено в',
        blank=True,
        null=True
    )
    
    error_message = models.TextField(
        verbose_name='Сообщение об ошибке',
        blank=True,
        null=True
    )
    
    # Автоматические поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Напоминание'
        verbose_name_plural = 'Напоминания'
        ordering = ['send_date']
        indexes = [
            models.Index(fields=['client', 'send_date']),
            models.Index(fields=['send_status']),
            models.Index(fields=['send_date']),
        ]
    
    def __str__(self):
        return f'Напоминание #{self.id} - {self.client.get_full_name()}'
    
    def is_overdue(self):
        """Просрочено ли напоминание"""
        return self.send_date < timezone.now() and self.send_status == 'pending'
    
    def can_send(self):
        """Можно ли отправить напоминание"""
        return self.send_status == 'pending' and self.send_date <= timezone.now()
    
    def mark_as_sent(self):
        """Пометить как отправленное"""
        self.send_status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message):
        """Пометить как неудачное"""
        self.send_status = 'failed'
        self.error_message = error_message
        self.sent_at = timezone.now()
        self.save()
    
    def get_reminder_type_display_name(self):
        """Получить отображаемое название типа напоминания"""
        return dict(self.REMINDER_TYPE_CHOICES).get(self.reminder_type, 'Неизвестно')
    
    def get_send_method_display_name(self):
        """Получить отображаемое название способа отправки"""
        return dict(self.SEND_METHOD_CHOICES).get(self.send_method, 'Неизвестно')