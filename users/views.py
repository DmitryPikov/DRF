from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User, PaymentCourse
from users.serializers import UserDetailSerializer, UserSerializer, PaymentCourseSerializer
from users.services import create_stripe_session, create_stripe_price


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserListAPIView(ListAPIView):
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


class UserRetrieveAPIView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def perform_update(self, serializer):
        user = serializer.save()
        if "password" in serializer.validated_data:
            user.set_password(serializer.validated_data["password"])
            user.save()


class UserDestroyAPIView(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


class PaymentCourseCreateAPIView(CreateAPIView):
    serializer_class = PaymentCourseSerializer
    queryset = PaymentCourse.objects.all()

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        amount_in_dollars = payment.amount
        price = create_stripe_price(amount_in_dollars)
        session_id, payment_link = create_stripe_session(price)
        payment.session_id = session_id
        payment.link = payment_link
        payment.save()
