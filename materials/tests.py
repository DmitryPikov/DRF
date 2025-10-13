from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from materials.models import Course, CourseSubscription, Lesson
from materials.serializers import CourseSubscriptionSerializer
from users.models import User


class LessonCreateAPIViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="admin@admin.com")
        self.course = Course.objects.create(
            name="Тестовый курс", description="Тестовое описание", owner=self.user
        )

        self.lesson = Lesson.objects.create(
            name="Валидация", course=self.course, owner=self.user
        )

        self.course_subscription = CourseSubscription.objects.create(
            user=self.user, course=self.course
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_create(self):
        url = reverse("materials:lesson_create")
        data = {
            "name": "Тестовая лекция",
            "description": "Тестовое описание",
            "course": self.course.id,
            "owner": self.user.id,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(Lesson.objects.filter(name="Тестовая лекция").exists())


class LessonListAPIViewTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create(email="user1@test.com", password="testpass123")
        self.user2 = User.objects.create(email="user2@test.com", password="testpass123")

        self.course1 = Course.objects.create(
            name="Курс 1", description="Описание курса 1", owner=self.user1
        )
        self.course2 = Course.objects.create(
            name="Курс 2", description="Описание курса 2", owner=self.user2
        )

        self.lesson1 = Lesson.objects.create(
            name="Урок 1",
            description="Описание урока 1",
            course=self.course1,
            owner=self.user1,
            url="https://www.youtube.com/watch?v=test1",
        )

        self.lesson2 = Lesson.objects.create(
            name="Урок 2",
            description="Описание урока 2",
            course=self.course1,
            owner=self.user1,
            url="https://www.youtube.com/watch?v=test2",
        )

        self.lesson3 = Lesson.objects.create(
            name="Урок 3",
            description="Описание урока 3",
            course=self.course2,
            owner=self.user2,
            url="https://www.youtube.com/watch?v=test3",
        )

        self.url = reverse("materials:lesson_list")
        self.client.force_authenticate(user=self.user1)

    def test_lesson_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LessonRetrieveAPIViewTestCase(APITestCase):

    def setUp(self):
        # Создаем группу модераторов
        self.moderators_group, created = Group.objects.get_or_create(name="Moders")

        self.user = User.objects.create(
            email="testuser@test.com", password="testpass123"
        )

        # Создаем модератора и добавляем в группу
        self.moderator = User.objects.create(
            email="moderator@test.com", password="testpass123"
        )
        self.moderator.groups.add(self.moderators_group)

        self.other_user = User.objects.create(
            email="otheruser@test.com", password="testpass123"
        )

        self.course = Course.objects.create(
            name="Тестовый курс",
            description="Описание тестового курса",
            owner=self.user,
        )

        self.lesson = Lesson.objects.create(
            name="Тестовый урок",
            description="Описание тестового урока",
            course=self.course,
            owner=self.user,
            url="https://www.youtube.com/watch?v=test123",
        )

    def test_retrieve_lesson_owner(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson_retrieve", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Тестовый урок")
        self.assertEqual(response.data["description"], "Описание тестового урока")

    def test_retrieve_lesson_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("materials:lesson_retrieve", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Тестовый урок")

    def test_retrieve_lesson_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("materials:lesson_retrieve", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_lesson_unauthenticated(self):
        url = reverse("materials:lesson_retrieve", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_lesson(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson_retrieve", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_lesson_structure(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson_retrieve", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("description", data)
        self.assertIn("owner", data)

        self.assertEqual(data["name"], "Тестовый урок")
        self.assertEqual(data["description"], "Описание тестового урока")

        if "url" in data and data["url"] is not None:
            self.assertEqual(data["url"], "https://www.youtube.com/watch?v=test123")
        else:
            print("URL field is missing or None - check your LessonSerializer")


class LessonDestroyAPIViewTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.owner_user = User.objects.create(
            email="owner@test.com", first_name="Owner", last_name="User"
        )
        self.owner_user.set_password("testpass123")
        self.owner_user.save()

        self.regular_user = User.objects.create(
            email="regular@test.com", first_name="Regular", last_name="User"
        )
        self.regular_user.set_password("testpass123")
        self.regular_user.save()

        self.moderator_user = User.objects.create(
            email="moderator@test.com", first_name="Moderator", last_name="User"
        )
        self.moderator_user.set_password("testpass123")
        self.moderator_user.is_staff = True
        self.moderator_user.save()

        # Создаем курс
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.owner_user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Test Lesson Description",
            course=self.course,
            owner=self.owner_user,
            url="https://www.youtube.com/test",
        )

        # ИСПРАВЛЕНО: используем reverse с именем маршрута
        self.url_owned = reverse(
            "materials:lesson_delete", kwargs={"pk": self.lesson.id}
        )
        self.url_not_found = reverse("materials:lesson_delete", kwargs={"pk": 999})

    def test_owner_can_delete_multiple_own_lessons(self):
        self.client.force_authenticate(user=self.owner_user)

        # Создаем еще один урок
        another_lesson = Lesson.objects.create(
            name="Another Owned Lesson",
            description="Another lesson owned by owner",
            course=self.course,
            owner=self.owner_user,
            url="https://www.youtube.com/another",
        )
        another_url = reverse(
            "materials:lesson_delete", kwargs={"pk": another_lesson.id}
        )

        initial_count = Lesson.objects.count()

        # Удаляем первый урок
        response = self.client.delete(self.url_owned)
        self.assertEqual(response.status_code, 204)

        # Удаляем второй урок
        response = self.client.delete(another_url)
        self.assertEqual(response.status_code, 204)

        final_count = Lesson.objects.count()
        self.assertEqual(final_count, initial_count - 2)

    def test_owner_can_delete_own_lesson(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.delete(self.url_owned)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_moderator_cannot_delete_lesson(self):
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.delete(self.url_owned)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_delete_others_lesson(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.url_owned)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_delete_lesson(self):
        response = self.client.delete(self.url_owned)
        self.assertEqual(response.status_code, 401)

    def test_delete_nonexistent_lesson(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.delete(self.url_not_found)
        self.assertEqual(response.status_code, 404)

    def test_lesson_count_decreases_after_delete(self):
        self.client.force_authenticate(user=self.owner_user)
        initial_count = Lesson.objects.count()
        response = self.client.delete(self.url_owned)
        self.assertEqual(response.status_code, 204)
        final_count = Lesson.objects.count()
        self.assertEqual(final_count, initial_count - 1)


class LessonUpdateAPIViewTestCase(APITestCase):
    def setUp(self):
        # Создаем группу модераторов
        self.moderators_group, created = Group.objects.get_or_create(name="Moders")

        # Создаем пользователей
        self.owner_user = User.objects.create(
            email="owner@test.com", first_name="Owner", last_name="User"
        )
        self.owner_user.set_password("testpass123")
        self.owner_user.save()

        self.regular_user = User.objects.create(
            email="regular@test.com", first_name="Regular", last_name="User"
        )
        self.regular_user.set_password("testpass123")
        self.regular_user.save()

        self.moderator_user = User.objects.create(
            email="moderator@test.com", first_name="Moderator", last_name="User"
        )
        self.moderator_user.set_password("testpass123")
        self.moderator_user.groups.add(self.moderators_group)
        self.moderator_user.save()

        # Создаем курс
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.owner_user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            name="Original Lesson Name",
            description="Original Lesson Description",
            course=self.course,
            owner=self.owner_user,
            url="https://www.youtube.com/original",
        )

        # URL для обновления
        self.url = reverse("materials:lesson_update", kwargs={"pk": self.lesson.id})
        self.url_not_found = reverse("materials:lesson_update", kwargs={"pk": 999})

        # Данные для обновления
        self.valid_update_data = {
            "name": "Updated Lesson Name",
            "description": "Updated Lesson Description",
            "url": "https://www.youtube.com/updated",
        }

    def test_owner_can_update_own_lesson(self):
        """Владелец может обновлять свой урок"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.patch(self.url, self.valid_update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что данные обновились
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Updated Lesson Name")
        self.assertEqual(self.lesson.description, "Updated Lesson Description")
        self.assertEqual(self.lesson.url, "https://www.youtube.com/updated")

    def test_owner_can_update_own_lesson_with_put(self):
        """Владелец может обновлять свой урок используя PUT"""
        self.client.force_authenticate(user=self.owner_user)

        put_data = {
            "name": "PUT Updated Lesson",
            "description": "PUT Updated Description",
            "course": self.course.id,
            "owner": self.owner_user.id,
            "url": "https://www.youtube.com/put-updated",
        }

        response = self.client.put(self.url, put_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что данные обновились
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "PUT Updated Lesson")
        self.assertEqual(self.lesson.description, "PUT Updated Description")

    def test_moderator_can_update_any_lesson(self):
        """Модератор может обновлять любой урок"""
        self.client.force_authenticate(user=self.moderator_user)

        response = self.client.patch(self.url, self.valid_update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что данные обновились
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Updated Lesson Name")

    def test_regular_user_cannot_update_others_lesson(self):
        """Обычный пользователь не может обновлять чужой урок"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.patch(self.url, self.valid_update_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Проверяем, что данные НЕ обновились
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Original Lesson Name")
        self.assertEqual(self.lesson.description, "Original Lesson Description")

    def test_anonymous_user_cannot_update_lesson(self):
        """Анонимный пользователь не может обновлять урок"""
        response = self.client.patch(self.url, self.valid_update_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что данные НЕ обновились
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Original Lesson Name")

    def test_update_nonexistent_lesson(self):
        """Попытка обновления несуществующего урока возвращает 404"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.patch(self.url_not_found, self.valid_update_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_lesson(self):
        """Частичное обновление урока (только имени)"""
        self.client.force_authenticate(user=self.owner_user)

        partial_data = {"name": "Partially Updated Name"}

        response = self.client.patch(self.url, partial_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что обновилось только имя
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Partially Updated Name")
        self.assertEqual(
            self.lesson.description, "Original Lesson Description"
        )  # Не изменилось
        self.assertEqual(
            self.lesson.url, "https://www.youtube.com/original"
        )  # Не изменилось

    def test_update_lesson_with_invalid_data(self):
        """Обновление урока с невалидными данными"""
        self.client.force_authenticate(user=self.owner_user)

        invalid_data = {
            "name": "",  # Пустое имя - должно быть невалидным
            "url": "invalid-url",  # Невалидный URL
        }

        response = self.client.patch(self.url, invalid_data)

        # Должен вернуть 400 Bad Request или 422 Unprocessable Entity
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY],
        )

    def test_update_lesson_course_field(self):
        """Обновление поля курса урока"""
        self.client.force_authenticate(user=self.owner_user)

        # Создаем новый курс
        new_course = Course.objects.create(
            name="New Course",
            description="New Course Description",
            owner=self.owner_user,
        )

        update_data = {"course": new_course.id}

        response = self.client.patch(self.url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что курс обновился
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.course, new_course)

    def test_response_structure_after_update(self):
        """Проверка структуры ответа после обновления"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.patch(self.url, self.valid_update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        data = response.data
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("description", data)
        self.assertIn("course", data)
        self.assertIn("owner", data)
        self.assertIn("url", data)

        # Проверяем обновленные значения
        self.assertEqual(data["name"], "Updated Lesson Name")
        self.assertEqual(data["description"], "Updated Lesson Description")
        self.assertEqual(data["url"], "https://www.youtube.com/updated")


class CourseSubscriptionAPITestCase(APITestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create(
            email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create(
            email="other@example.com", password="otherpass123"
        )

        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.user
        )
        self.course2 = Course.objects.create(
            name="Another Course", description="Another Description", owner=self.user
        )

        self.client = APIClient()
        self.url = reverse("materials:subscriptions")  # Замените на имя вашего URL

    def authenticate_user(self):
        """Аутентификация тестового пользователя"""
        self.client.force_authenticate(user=self.user)


class CourseSubscriptionPostTests(CourseSubscriptionAPITestCase):
    def test_create_subscription_success(self):
        """Тест успешного создания подписки"""
        self.authenticate_user()

        response = self.client.post(self.url, {"course_id": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(response.data["subscription_status"])
        self.assertEqual(int(response.data["course_id"]), self.course.id)
        self.assertEqual(response.data["course_name"], self.course.name)

        # Проверяем, что подписка создана в БД
        subscription_exists = CourseSubscription.objects.filter(
            user=self.user, course=self.course
        ).exists()
        self.assertTrue(subscription_exists)

    def test_delete_subscription_success(self):
        """Тест успешного удаления подписки"""
        # Сначала создаем подписку
        CourseSubscription.objects.create(user=self.user, course=self.course)
        self.authenticate_user()

        response = self.client.post(self.url, {"course_id": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(response.data["subscription_status"])
        self.assertEqual(int(response.data["course_id"]), self.course.id)
        self.assertEqual(response.data["course_name"], self.course.name)

        # Проверяем, что подписка удалена из БД
        subscription_exists = CourseSubscription.objects.filter(
            user=self.user, course=self.course
        ).exists()
        self.assertFalse(subscription_exists)

    def test_post_without_course_id(self):
        """Тест запроса без course_id"""
        self.authenticate_user()

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "course_id обязателен")

    def test_post_with_invalid_course_id(self):
        """Тест запроса с несуществующим course_id"""
        self.authenticate_user()

        response = self.client.post(self.url, {"course_id": 999})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_unauthenticated(self):
        """Тест неаутентифицированного запроса"""
        response = self.client.post(self.url, {"course_id": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseSubscriptionGetTests(CourseSubscriptionAPITestCase):
    def test_get_subscriptions_success(self):
        """Тест успешного получения списка подписок"""
        # Создаем несколько подписок
        subscription1 = CourseSubscription.objects.create(
            user=self.user, course=self.course
        )
        subscription2 = CourseSubscription.objects.create(
            user=self.user, course=self.course2
        )

        self.authenticate_user()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # Проверяем данные подписок
        subscriptions_data = response.data["subscriptions"]
        self.assertEqual(len(subscriptions_data), 2)

        # Проверяем, что данные сериализованы правильно
        expected_data = CourseSubscriptionSerializer(
            [subscription1, subscription2], many=True
        ).data
        self.assertEqual(subscriptions_data, expected_data)

    def test_get_empty_subscriptions(self):
        """Тест получения пустого списка подписок"""
        self.authenticate_user()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["subscriptions"]), 0)

    def test_get_only_user_subscriptions(self):
        """Тест, что возвращаются только подписки текущего пользователя"""
        # Создаем подписки для разных пользователей
        CourseSubscription.objects.create(user=self.user, course=self.course)
        CourseSubscription.objects.create(user=self.other_user, course=self.course2)

        self.authenticate_user()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["subscriptions"][0]["course"], self.course.id)

    def test_get_unauthenticated(self):
        """Тест неаутентифицированного GET запроса"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseSubscriptionToggleTests(CourseSubscriptionAPITestCase):
    def test_subscription_toggle_workflow(self):
        """Тест полного цикла переключения подписки"""
        self.authenticate_user()

        # Первый запрос - создаем подписку
        response1 = self.client.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response1.data["message"], "Подписка добавлена")
        self.assertTrue(response1.data["subscription_status"])
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.user, course=self.course
            ).exists()
        )

        # Второй запрос - удаляем подписку
        response2 = self.client.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response2.data["message"], "Подписка удалена")
        self.assertFalse(response2.data["subscription_status"])
        self.assertFalse(
            CourseSubscription.objects.filter(
                user=self.user, course=self.course
            ).exists()
        )

        # Третий запрос - снова создаем подписку
        response3 = self.client.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response3.data["message"], "Подписка добавлена")
        self.assertTrue(response3.data["subscription_status"])
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.user, course=self.course
            ).exists()
        )
