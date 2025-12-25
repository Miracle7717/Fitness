from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Кастомная модель пользователя с ролями"""

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        MANAGER = 'manager', _('Менеджер')
        TRAINER = 'trainer', _('Тренер')
        RECEPTION = 'reception', _('Администратор рецепции')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTION,
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]

    @property
    def is_trainer(self):
        return self.role == self.Role.TRAINER

    @property
    def is_reception(self):
        return self.role == self.Role.RECEPTION