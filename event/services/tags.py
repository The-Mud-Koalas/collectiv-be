from ..models import Tags


def handle_get_all_tags():
    return Tags.objects.all()

