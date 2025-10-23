from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def check_inactive_users():
    try:
        one_month_ago = timezone.now() - timedelta(days=30)

        inactive_users = User.objects.filter(
            last_login__lt=one_month_ago,
            is_active=True
        )

        users_count = inactive_users.count()

        result = inactive_users.update(is_active=False)

        return {
            'status': 'success',
            'message': f'Заблокировано {result} неактивных пользователей',
            'users_blocked': result,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f'Ошибка в задаче check_inactive_users: {str(e)}')
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': timezone.now().isoformat()
        }
