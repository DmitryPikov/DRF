from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = SerializerMethodField()

    def get_count_of_lessons_in_course(self, obj):
        return Lesson.objects.filter(course=obj).count()

    def get_lessons(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        return LessonSerializer(lessons, many=True).data

    class Meta:
        model = Course
        fields = ("name", "description", "count_lessons_in_course", "lessons")


class CourseDetailSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = SerializerMethodField()

    def get_count_of_lessons_in_course(self, obj):
        return Lesson.objects.filter(course=obj).count()

    def get_lessons(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        return LessonSerializer(lessons, many=True).data

    class Meta:
        model = Course
        fields = []


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
