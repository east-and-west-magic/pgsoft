"""
Generate hash code with MD5 algorithm

"""

import hashlib


def md5(value: object):
    """generate a md5 hash string

    Args:
        value: a stringlizable object

    Returns:
        str: a hash string with hex digits
    """
    hsh = hashlib.md5()
    hsh.update(str(value).encode("utf-8"))
    return hsh.hexdigest()
