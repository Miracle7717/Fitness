import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_club.settings')
django.setup()

from django.contrib.auth.models import User

def create_users():
    print("Создание тестовых пользователей...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@fitness.com',
            'first_name': 'Админ',
            'last_name': 'Админов',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'manager',
            'email': 'manager@fitness.com',
            'first_name': 'Мария',
            'last_name': 'Менеджерова',
            'password': 'manager123',
            'is_staff': True,
        },
        {
            'username': 'trainer',
            'email': 'trainer@fitness.com',
            'first_name': 'Иван',
            'last_name': 'Тренеров',
            'password': 'trainer123',
        },
        {
            'username': 'reception',
            'email': 'reception@fitness.com',
            'first_name': 'Ольга',
            'last_name': 'Ресепшенова',
            'password': 'reception123',
        },
    ]
    
    for data in users_data:
        password = data.pop('password')
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Создан пользователь: {user.username}")
        else:
            print(f"Пользователь уже существует: {user.username}")
    
    print("\nТестовые пользователи созданы!")

if __name__ == '__main__':
    create_users()