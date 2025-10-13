from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from materials.models import Course, CourseSubscription, Lesson
from materials.validators import validate_link


class CourseSerializer(serializers.ModelSerializer):
    count_lessons_in_course = serializers.SerializerMethodField()
    lessons = SerializerMethodField()

    def get_count_of_lessons_in_course(self, obj):
        return Lesson.objects.filter(course=obj).count()

    def get_lessons(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        return LessonSerializer(lessons, many=True).data

    class Meta:
        model = Course
        fields = ("name", "description", "count_lessons_in_course", "lessons")


class CourseDetailSerializer(serializers.ModelSerializer):
    count_lessons_in_course = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()

    def get_count_of_lessons_in_course(self, obj):
        return Lesson.objects.filter(course=obj).count()

    def get_lessons(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        return LessonSerializer(lessons, many=True).data

    class Meta:
        model = Course
        fields = []


class LessonSerializer(serializers.ModelSerializer):
    url = serializers.URLField(
        validators=[validate_link], required=False, allow_blank=True
    )

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = CourseSubscription
        fields = ["id", "user", "course", "course_title", "user_email"]
        read_only_fields = ["id"]
