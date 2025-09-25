from django.db import models


class Course(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название курса",
        help_text="Введите название курса",
    )
    photo = models.ImageField(
        upload_to="courses/photo/",
        verbose_name="Фото курса",
        help_text="Загрузите фото курса",
        null=True,
        blank=True,
    )
    description = models.TextField(
        max_length=1000,
        verbose_name="Описание курса",
        help_text="Введите описание курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название урока",
        help_text="Введите название урока",
    )
    description = models.TextField(
        max_length=1000,
        verbose_name="Описание урока",
        help_text="Введите описание урока",
    )
    photo = models.ImageField(
        upload_to="lessons/photo/",
        verbose_name="Фото урока",
        help_text="Загрузите фото урока",
        null=True,
        blank=True,
    )
    url = models.URLField(
        verbose_name="Ссылка на видео",
        help_text="Введите ссылку на видео",
        null=True,
        blank=True,
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, verbose_name="Курс", help_text="Выберите курс"
    )
