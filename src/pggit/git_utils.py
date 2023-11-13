"""a module implemented with subprocess module,
providing some tools to manage repository
"""

import os
import subprocess
from typing import Union
import re


def is_repo_root(path: str) -> bool:
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


def git_reset(rootdir: str) -> bool:
    """forcely reset the repository to HEAD^ version.

    Args:
        rootdir: the root directory of a repository

    Returns:
        bool: succeed or not
    """
    if not os.path.exists(rootdir):
        print("[git_reset] error: rootdir not exists")
        return False
    if not is_repo_root(rootdir):
        print(f"[git_reset] error: {rootdir} is not a repo")
        return False

    try:
        # stage all before reset
        command = ["git", "add", "."]
        code = subprocess.call(command, cwd=rootdir)
        if code:
            print(f"[git_reset] error: return code {code} while adding")
            return False
        # reset
        command = ["git", "reset", "--hard", "HEAD^"]
        code = subprocess.call(command, cwd=rootdir)
        if code:
            print(f"[git_reset] error: return code {code} while resetting")
            return False
        return True
    except Exception as e:
        print(f"[git_reset_hard] error: {e}")
        return False


def git_config(rootdir: str, key: str, value: str) -> bool:
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


def git_diff_files(rootdir: str, beforeId: str, afterId: str):
    """get changed files' name and their status between two commits,
        from beforeId to afterId

    Args:
        rootdir (str): the root directory of the repository
        beforeId (str): the commit id earlier committed
        afterId (str): the commit id later committed

    Returns:
        dict[str, str] | None: if succeed return a dict with
        changed files' name as key and their status as value
        possible statuses are as following:
        - D: deleted file
        - M: modified file
        - A: newly added file
    """
    if not os.path.exists(rootdir):
        print("[git_diff_files] error: rootdir not exists")
        return None
    if not is_repo_root(rootdir):
        print(f"[git_diff_files] error: {rootdir} is not a repo")
        return None

    try:
        command = ["git", "diff", beforeId, afterId, "--name-status"]
        res = subprocess.check_output(command, cwd=rootdir).decode("utf-8")
        res = res.replace("/", os.sep).splitlines()
    except Exception as e:
        print(f"[git_diff_files] error: {e}")
        return None
    outp = {}
    for line in res:
        line = line.split("\t")
        status = line[0].strip()
        filename = line[1].strip('" ')
        outp[filename] = status
    return outp


def git_diff_content(rootdir: str, filepath: str, beforeId: str, afterId: str):
    """get difference content of a single file between two commits

    Args:
        beforeId (str): the commit id earlier committed
        afterId (str): the commit id later committed

    Returns:
    - if succeed,return a dict with structure as following:

    ```
    {
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
        print("[git_diff_content] error: rootdir not exists")
        return None
    if not is_repo_root(rootdir):
        print(f"[git_diff_content] error: {rootdir} is not a repo")
        return None

    command = ["git", "diff", beforeId, afterId, filepath]
    try:
        res = subprocess.check_output(command, cwd=rootdir).decode("utf-8")
        res = res.replace("/", os.sep).splitlines()
    except Exception as e:
        print(f"[git_diff_content] error: {e}")
        return None

    outp = dict[str, dict[int, str]]()
    oldcur = 1
    newcur = 1
    for line in res:
        if line.startswith("@@"):
            tmp = line.split()
            oldcur = int(tmp[1].strip("-").split(",")[0])
            newcur = int(tmp[2].strip("-").split(",")[0])
            continue
        if line.startswith("-"):
            if "delline" not in outp:
                outp["delline"] = {}
            outp["delline"][oldcur] = line[1:]
            oldcur += 1
            continue
        if line.startswith("+"):
            if "addline" not in outp:
                outp["addline"] = {}
            outp["addline"][newcur] = line[1:]
            newcur += 1
            continue
        oldcur += 1
        newcur += 1
    return outp
