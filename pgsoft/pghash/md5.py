"""
Generate hash code with MD5 algorithm

"""

import hashlib


def md5(obj: object):
    """generate a md5 hash string

    Args:
        value: a stringlizable object

    Returns:
        str: a hash string with hex digits
    """

    if isinstance(obj, dict):
        obj = sort_dict(obj)
    hsh = hashlib.md5()
    hsh.update(str(obj).encode("utf-8"))
    return hsh.hexdigest()


def sort_dict(obj: dict):
    """sort items of a dict, including its sub dict

    Returns:
        return a ordered dict
    """
    for key, value in obj.items():
        if isinstance(value, dict):
            obj[key] = sort_dict(value)
    itms = list(obj.items())
    try:
        itms.sort()
    except Exception:
        itms.sort(key=lambda a, b: str(a[1]) > str(b[1]))
    return dict(itms)


if __name__ == "__main__":
    val1 = {
        "a": {
            "a": 1,
            "b": 2,
            "c": {
                "a": {
                    "a": 1,
                    "b": 2,
                    "c": {
                        "a": {
                            "a": 1,
                            "b": 2,
                            "c": {"a": {"a": 1, "b": 2}, "b": "a and b"},
                        },
                        "b": "a and b",
                    },
                },
                "b": "a and b",
            },
        },
        "b": "a and b",
    }
    val2 = {
        "b": "a and b",
        "a": {
            "b": 2,
            "a": 1,
            "c": {
                "b": "a and b",
                "a": {
                    "b": 2,
                    "a": 1,
                    "c": {
                        "b": "a and b",
                        "a": {
                            "b": 2,
                            "a": 1,
                            "c": {"b": "a and b", "a": {"b": 2, "a": 1}},
                        },
                    },
                },
            },
        },
    }
    print(md5(val1) == md5(val2))
