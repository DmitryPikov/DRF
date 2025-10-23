from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import CourseSubscription, Course


@shared_task
def send_course_update_notification(course_id):
    try:
        course = Course.objects.get(id=course_id)

        if not course.should_send_notification():
            return f"Уведомление для курса '{course.name}' не отправлено - прошло менее 4 часов с предыдущего уведомления"

        subscriptions = CourseSubscription.objects.filter(course=course)

        if not subscriptions.exists():
            return f"Нет подписчиков для курса '{course.name}'"

        email_count = 0
        for subscription in subscriptions:
            try:
                send_mail_update_course([subscription.user.email])
                email_count += 1
            except Exception as e:
                print(f"Ошибка отправки для {subscription.user.email}: {str(e)}")

        course.last_notification_sent = timezone.now()
        course.save()

        return f"Уведомления отправлены {email_count} подписчикам курса '{course.name}'"

    except Course.DoesNotExist:
        return f"Курс с id {course_id} не найден"
    except Exception as e:
        return f"Ошибка при отправке уведомлений: {str(e)}"


@shared_task
def send_mail_update_course(email):
    send_mail('Курс обновлен', 'Курс обновлен', settings.EMAIL_HOST_USER, [email])
