import stripe
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_price(amount):

    price = stripe.Price.create(
        currency="usd",
        unit_amount=amount * 100,
        product_data={"name": "Payment course"},
    )

    return price


def create_stripe_session(price):
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )

    return session.get("id"), session.get("url")


def create_periodic_task():
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='3',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
        timezone='Europe/Moscow'
    )

    PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name='Check inactive users',
        task='users.tasks.check_inactive_users',
        defaults={
            'description': 'Блокировка пользователей, не заходивших более месяца',
            'enabled': True
        }
    )
