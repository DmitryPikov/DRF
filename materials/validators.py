from rest_framework.serializers import ValidationError


def validate_link(link):
    if "youtube.com" not in link:
        raise ValidationError("Link is not valid")
