from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView, get_object_or_404)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, CourseSubscription, Lesson
from materials.paginations import CustomPagination
from materials.serializers import (CourseSerializer,
                                   CourseSubscriptionSerializer,
                                   LessonSerializer)
from materials.tasks import send_course_update_notification
from users.models import Payment
from users.permissions import IsModer, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (~IsModer,)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == "destroy":
            self.permission_classes = (~IsModer | IsOwner,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()

        if instance.should_send_notification():
            send_course_update_notification.delay(instance.id)

        return instance

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def notification_status(self, request, pk=None):
        course = self.get_object()
        can_send = course.should_send_notification()

        if course.last_notification_sent:
            time_since_last = timezone.now() - course.last_notification_sent
            hours_since_last = time_since_last.total_seconds() / 3600
            next_notification_in = max(0, 4 - hours_since_last)
        else:
            hours_since_last = None
            next_notification_in = 0

        return Response({
            "course_id": course.id,
            "course_name": course.name,
            "can_send_notification": can_send,
            "last_notification_sent": course.last_notification_sent,
            "hours_since_last_notification": hours_since_last,
            "next_notification_in_hours": next_notification_in
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def send_test_notification(self, request, pk=None):
        course = self.get_object()

        if not course.should_send_notification():
            return Response({
                "error": "Нельзя отправить уведомление - прошло менее 4 часов с предыдущего",
                "last_notification_sent": course.last_notification_sent,
                "next_notification_available_in_hours": max(0, 4 - (
                            timezone.now() - course.last_notification_sent).total_seconds() / 3600)
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        task_result = send_course_update_notification.delay(course.id)

        return Response({
            "message": "Задача на отправку уведомлений запущена",
            "task_id": task_result.id,
            "course_id": course.id,
            "course_name": course.name
        })


class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (~IsModer, IsAuthenticated)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CustomPagination


class LessonRetrieveAPIView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsModer)


class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsOwner | ~IsModer)


class LessonUpdateAPIView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsModer)

    def perform_update(self, serializer):
        instance = serializer.save()

        if instance.course:
            if instance.course.should_send_notification():
                send_course_update_notification.delay(instance.course.id)

        return instance


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ("payment_date", "paid_course", "payment_method")
    ordering_fields = ("payment_date",)


class CourseSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        subscription_exists = CourseSubscription.objects.filter(
            user=user, course=course
        ).exists()

        if subscription_exists:
            CourseSubscription.objects.filter(user=user, course=course).delete()
            message = "Подписка удалена"
            subscription_status = False
        else:
            subscription = CourseSubscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            subscription_status = True

            serializer = CourseSubscriptionSerializer(subscription)

        return Response(
            {
                "message": message,
                "subscription_status": subscription_status,
                "course_id": course_id,
                "course_name": course.name,
            }
        )

    def get(self, request, *args, **kwargs):
        user = request.user
        subscriptions = CourseSubscription.objects.filter(user=user)
        serializer = CourseSubscriptionSerializer(subscriptions, many=True)

        return Response(
            {"count": subscriptions.count(), "subscriptions": serializer.data}
        )
