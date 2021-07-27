from django.http import QueryDict

from ..utils import dict_to_query_dict


def test_dict_to_query_dict():
    output = dict_to_query_dict({})
    assert output == QueryDict("")

    output = dict_to_query_dict({"a": "b"})
    assert output == QueryDict("a=b")

    output = dict_to_query_dict({"a": ["b", "c"]})
    assert output == QueryDict("a=b&a=c")

    output = dict_to_query_dict({"a": ["b", "c"], "d": "e"})
    assert output == QueryDict("a=b&a=c&d=e")
