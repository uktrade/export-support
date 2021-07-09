import random

from django.conf import settings
from django.http import QueryDict


def get_reference_number():
    return "".join(
        random.choice(settings.REFERENCE_NUMBER_ALPHABET)
        for _ in range(settings.REFERENCE_NUMBER_SIZE)
    )


def dict_to_query_dict(a_dict):
    params = QueryDict(mutable=True)
    for key, value in a_dict.items():
        if isinstance(value, list):
            params.setlist(key, value)
        else:
            params[key] = value

    return params
