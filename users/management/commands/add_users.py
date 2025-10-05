from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Add users"

    def handle(self, *args, **options):
        users = [
            {
                "first_name": "Иван",
                "last_name": "Иванов",
                "email": "ivan@example.com",
                "phone": "+79991234567",
                "city": "Москва",
            },
            {
                "first_name": "Петр",
                "last_name": "Петров",
                "email": "petr@example.com",
                "phone": "+79997654321",
                "city": "Санкт-Петербург",
            },
            {
                "first_name": "Мария",
                "last_name": "Сидорова",
                "email": "maria@example.com",
                "phone": "+79995556677",
                "city": "Казань",
            },
        ]

        for user in users:
            user, created = User.objects.get_or_create(**user)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Payment {user} created."))
            else:
                self.stdout.write(self.style.WARNING(f"Payment {user} already exists."))
