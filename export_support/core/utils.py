from django.http import QueryDict


def dict_to_query_dict(a_dict):
    params = QueryDict(mutable=True)
    for key, value in a_dict.items():
        if isinstance(value, list):
            params.setlist(key, value)
        else:
            params[key] = value

    return params
