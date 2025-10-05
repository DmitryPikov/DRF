from django.core.management import BaseCommand
from django.utils import timezone

from materials.models import Course
from users.models import Payment, User


class Command(BaseCommand):
    help = "Add payments"

    def handle(self, *args, **options):
        payments = [
            {
                "user": User.objects.get(id=1),
                "payment_date": "2023-01-01",
                "paid_course": Course.objects.get(id=1),
                "amount": 5000,
                "payment_method": "Наличными",
            },
            {
                "user": User.objects.get(id=2),
                "payment_date": "2023-01-02",
                "paid_course": Course.objects.get(id=1),
                "amount": 5000,
                "payment_method": "Наличными",
            },
            {
                "user": User.objects.get(id=3),
                "payment_date": "2023-01-03",
                "paid_course": Course.objects.get(id=1),
                "amount": 5000,
                "payment_method": "Наличными",
            },
        ]

        for payment in payments:
            payment, created = Payment.objects.get_or_create(**payment)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Payment {payment} created."))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Payment {payment} already exists.")
                )
