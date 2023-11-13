"""a module implemented with subprocess module,
providing some tools to manage repository
"""

import os
import subprocess
from typing import Union
import re


def is_repo_root(path: str):
    """check if the path is a root directory of a repository

    Args:
        path (str): a existed path

    Returns:
        bool: True if it's a repo
    """

    try:
        if not os.path.exists(path):
            print("[is_repo_root] error: No such directory")
            return False
        command = ["git", "-C", path, "rev-parse", "--show-toplevel"]
        root = subprocess.check_output(command).decode("utf-8").strip("\n")
        if os.path.samefile(root, path):
            return True
    except Exception as e:
        print(f"[is_repo_root]: {e}")
    return False


def git_reset_hard(rootdir: str, commitid: str = "HEAD"):
    """forcely reset the repository to a committed version.

    Args:
        rootdir: the root directory of a repository
        commitid: a existed commit id

    Returns:
        bool: succeed or not
    """
    if not os.path.exists(rootdir):
        print("[git_reset_hard] error: rootdir not exists")
        return False
    if not is_repo_root(rootdir):
        print(f"[git_reset_hard] error: {rootdir} is not a repo")
        return False

    try:
        # stage all before reset
        command = ["git", "add", "."]
        subprocess.call(command, cwd=rootdir)
        # reset
        command = ["git", "reset", "--hard", commitid]
        subprocess.call(command, cwd=rootdir)
        return True
    except Exception as e:
        print(f"[git_reset_hard]: {e}")
        return False


def git_diff_all(rootdir: str, beforeId: str, afterId: str, nameonly: bool = True):
    """get differences between two commit, from beforeId to afterId

    Args:
        rootdir (str): the root directory of the repository
        beforeId (str): the commit id earlier committed
        afterId (str): the commit id later committed
        nameonly (bool, optional): whether only get names of files in differences,
        or get detailed diff info. Defaults to True.

    Returns:
        (list | dict):
    - if succeed,
        - if nameonly is True: return files changed(relative pathes) as a list
        - else: return a dict with structure as following:

    ```
    {
        "filename1":{
            "newfile": "filename",    #this is a new file
            "delfile": "filename",    # this file was deleted
            "rename": "new filename", # the key "filename" is an old name
            "delline": {lineindex1:"linestring1",
                        ...
                        lineindexn:"linestringn"}, # deleted lines
            "addline": {lineindex1:"linestring1",
                        ...
                        lineindexn:"linestringn"},  # added lines
            # not all these keys are included here, depending on diff info
        }
        ...
    }
    ```
    - if failed, return None
    """
    if not os.path.exists(rootdir):
        print("[git_diff_all] error: rootdir not exists")
        return None
    if not is_repo_root(rootdir):
        print(f"[git_diff_all] error: {rootdir} is not a repo")
        return None

    try:
        command = ["git", "diff", beforeId, afterId]
        command += ["--name-only"] if nameonly else []
        res = subprocess.check_output(command, cwd=rootdir).decode("utf-8")
        res = res.replace("/", os.sep).splitlines()
    except Exception as e:
        print(f"[git_diff] error: {e}")
        return None
    if nameonly:
        outp = res
    else:
        outp = {}
        for filepath in res:
            outp[filepath] = git_diff_file(filepath, beforeId, afterId)
    return outp


def git_config(rootdir: str, key: str, value: str):
    """set a configure value"""
    if not os.path.exists(rootdir):
        print("[git_config] error: rootdir not exists")
        return False
    if not is_repo_root(rootdir):
        print(f"[git_config] error: {rootdir} is not a repo")
        return False
    try:
        command = ["git", "config", key, value]
        subprocess.call(command, cwd=rootdir)
        return True
    except Exception as e:
        print(f"[git_config] error: {e}")
        return False


def git_diff_file(rootdir: str, filepath: str, beforeId: str, afterId: str):
    """get diff info of a single file between two commits

    Args:
        beforeId (str): the commit id earlier committed
        afterId (str): the commit id later committed

    Returns:
    - if succeed,return a dict with structure as following:

    ```
    {
        "newfile": "filename",    # name of the new file
        "delfile": "filename",    # name of the deleted file
        "rename": "filename",     # the new name of the file
        "delline": {lineindex1:"linestring1",
                    ...
                    lineindexn:"linestringn"}, # deleted lines
        "addline": {lineindex1:"linestring1",
                    ...
                    lineindexn:"linestringn"},  # added lines
        # not all these keys are included here, depending on diff info
    }
    ```
    - if failed, return None
    """
    if not os.path.exists(rootdir):
        print("[git_diff_file] error: rootdir not exists")
        return None
    if not is_repo_root(rootdir):
        print(f"[git_diff_file] error: {rootdir} is not a repo")
        return None

    command = ["git", "diff", beforeId, afterId, filepath]
    try:
        res = subprocess.check_output(command, cwd=rootdir).decode("utf-8")
        res = res.replace("/", os.sep).splitlines()
    except Exception as e:
        print(f"[git_diff_file] error: {e}")
        return None

    outp = dict[str, Union[str, dict[int, str]]]()
    a = ""
    b = ""
    old = {"start": 1, "len": 0, "cur": 1}
    new = {"start": 1, "len": 0, "cur": 1}
    for line in res:
        if line.startswith("diff"):
            tmp = re.match('.*a/(.*) .*b/(.*)"?', line).groups()
            a = tmp[0].strip('"')
            b = tmp[1].strip('"')
            if a != b:
                outp["rename"] = b
                break
        if line.startswith("---"):
            tmpa = line.split()[1]
            if tmpa == "/dev/null":
                outp["newfile"] = b
                break
        if line.startswith("+++"):
            tmpb = line.split()[1]
            if tmpb == "/dev/null":
                outp["delfile"] = a
                break
        if line.startswith("@@"):
            tmp = line.split()
            tmpa = map(int, tmp[1].strip("-").split(","))
            tmpb = map(int, tmp[2].strip("+").split(","))
            old["start"], old["len"], old["cur"] = tmpa[0], tmpa[1], tmpa[0]
            new["start"], new["len"], new["cur"] = tmpb[0], tmpb[1], tmpb[0]
            continue
        if line.startswith("-"):
            if "delline" not in outp:
                outp["delline"] = {}
            outp["delline"][old["cur"]] = line[1:]
            old["cur"] += 1
            continue
        if line.startswith("+"):
            if "addline" not in outp:
                outp["addline"] = {}
            outp["addline"][new["cur"]] = line[1:]
            new["cur"] += 1
            continue
        old["cur"] += 1
        new["cur"] += 1
    return outp
