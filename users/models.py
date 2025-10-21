from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите телефон",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    PAYMENT_METHODS_CHOICES = (("cash", "Наличными"), ("card", "Перевод на счет"))

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="payments",
    )
    payment_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата оплаты", help_text="Дата оплаты"
    )
    paid_course = models.ForeignKey(
        "materials.Course",
        on_delete=models.CASCADE,
        verbose_name="Оплаченный курс",
        blank=True,
        null=True,
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма", help_text="Сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS_CHOICES,
        verbose_name="Способ оплаты",
        help_text="Способ оплаты",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]


class PaymentCourse(models.Model):
    amount = models.PositiveIntegerField(
        verbose_name="Сумма курса", help_text="Укажите сумму курса",
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии",
        help_text="Укажите ID сессии",
    )
    link = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
        help_text="Укажите ссылку на оплату",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )

    class Meta:
        verbose_name = "Оплата курса"
        verbose_name_plural = "Оплаты курсов"

    def __str__(self):
        return self.amount
