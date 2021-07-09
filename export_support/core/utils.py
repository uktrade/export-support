import random

from django.conf import settings


def get_reference_number():
    return "".join(
        random.choice(settings.REFERENCE_NUMBER_ALPHABET)
        for _ in range(settings.REFERENCE_NUMBER_SIZE)
    )
