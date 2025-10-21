from rest_framework.serializers import ModelSerializer

from users.models import User, PaymentCourse


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class PaymentCourseSerializer(ModelSerializer):
    class Meta:
        model = PaymentCourse
        fields = "__all__"
