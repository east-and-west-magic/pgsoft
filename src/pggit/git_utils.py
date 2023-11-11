"""a module implemented with subprocess module,
providing some tools to manage repository
"""

import os
import subprocess
from typing import Sequence, Literal
import re


def is_repo_root(path: str):
    """check if the path is a root directory of a repository

    Args:
        path (str): a existed path

    Returns:
        bool: True if it's a repo
    """
    if not os.path.exists(path):
        print(f'[is_repo] error: directory "{path}" not exists')
        return False

    command = ["git", "-C", path, "rev-parse", "--show-toplevel"]
    try:
        rootdir = subprocess.check_output(command).decode("utf-8").strip("\n")
        if os.path.samefile(rootdir, path):
            return True
    except Exception as e:
        print(f"[git_add] error: {e}")
    return False


def git_add(rootdir: str, files: str | Sequence[str] = "."):
    """stage the changes in these files since last stage

    Args:
        rootdir (str): root directory of the repository.
        files (str | Sequence[str], optional): a single file or
            a list of files to be added. Defaults to ".", which means adding all.

    Returns:
        bool: True if succeed
    """
    if not os.path.exists(rootdir):
        print(f'[git_add] error: directory "{rootdir}" not exists')
        return False
    if not is_repo_root(rootdir):
        print(f"[git_add] error: {rootdir} is not a repo")
        return False

    command = ["git", "add"]
    if files != ".":
        filelist = []
        if isinstance(files, str):
            if not os.path.exists(files):
                print(f"[git_add] error: {files} not exists")
                return False
            filelist.append(files)
        elif isinstance(files, Sequence):
            for file in files:
                if not os.path.exists(files):
                    print(f"[git_add] error: {files} not exists")
                    return False
                filelist.append(file)
        else:
            print("[git_add] error: unsupported type of 'files' argument")
            return False
        if not filelist:
            print("[git_add] error: empty 'files' argument")
            return False
        command += filelist
    else:
        command += [files]

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        subprocess.call(command)
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"[git_add] error: {e}")
        os.chdir(cwd)
        return False


def git_reset(rootdir: str, commitid: str = "HEAD", hard: bool = False):
    """reset the repository to an ever commit version.

    Args:
        rootdir (str): root directory of the repository.
        commitid (str, optional): a valid commit id. Defaults to "HEAD".
        hard (bool, optional): whether reset forcely. Defaults to False.
            if False, unstage the staged changes, do nothing
                to untracked files in workspace
            if True, forcely delete all staged changes produced after
                the commit ,including untracked files

    Returns:
        bool: succeed or not
    """
    if not os.path.exists(rootdir):
        print(f'[git_reset] error: directory "{rootdir}" not exists')
        return False
    if not is_repo_root(rootdir):
        print(f"[git_reset] error: {rootdir} is not a repo")
        return False

    command = ["git", "reset"]
    if hard:
        command += ["--hard"]
    command += [commitid]

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        if hard:
            # track and stage all files before reset
            subprocess.call(["git", "add", "."])
        subprocess.call(command)
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"[git_reset] error: {e}")
        os.chdir(cwd)
        return False


def git_diff(rootdir: str, beforeId: str, afterId: str, nameonly: bool = True):
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
                    "delline": ["line1",...], # deleted lines
                    "addline": ["line1",...]  # added lines
                    # not all these keys are included here, depending on diff info
                }
                ...
            }
        ```
        - if failed, return None
    """
    if not os.path.exists(rootdir):
        print(f'[git_diff] error: directory "{rootdir}" not exists')
        return None
    if not is_repo_root(rootdir):
        print(f"[git_diff] error: {rootdir} is not a repo")
        return None

    command = ["git", "diff"]
    if nameonly:
        command += ["--name-only"]
    command += [beforeId, afterId]

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        res = subprocess.check_output(command).decode("utf-8")
        res = res.replace("/", os.sep).splitlines()
    except Exception as e:
        print(f"[git_diff] error: {e}")
        os.chdir(cwd)
        return None
    if nameonly:
        outp = res
    else:
        outp = dict[str, dict]()
        a = ""
        b = ""
        for i in range(len(res)):
            line = res[i]
            if line.startswith("diff"):
                tmp = re.match('.*a/(.*) .*b/(.*)"?', line).groups()
                a = tmp[0].strip('"')
                b = tmp[1].strip('"')
                if a != b:
                    outp[a] = {"rename": b}
                    while i + 1 < len(res) and (not res[i + 1].startswith("diff")):
                        i += 1
                    continue
            if line.startswith("---"):
                tmpa = line.split()[1]
                if tmpa == "/dev/null":
                    outp[b] = {"newfile": b}
                    while i + 1 < len(res) and (not res[i + 1].startswith("diff")):
                        i += 1
                    continue
            if line.startswith("+++"):
                tmpb = line.split()[1]
                if tmpb == "/dev/null":
                    outp[a] = {"delfile": a}
                    while i + 1 < len(res) and (not res[i + 1].startswith("diff")):
                        i += 1
                    continue
            if a not in outp:
                outp[a] = dict[str, list]()
            if line.startswith("-"):
                if "delline" not in outp[a]:
                    outp[a]["delline"] = []
                outp[a]["delline"].append(line[1:])
            if line.startswith("+"):
                if "addline" not in outp[a]:
                    outp[a]["addline"] = []
                outp[a]["addline"].append(line[1:])

    os.chdir(cwd)
    return outp


def git_head_hash(rootdir: str):
    """get the commit id of HEAD pointer"""
    if not os.path.exists(rootdir):
        print(f'[git_head_hash] error: directory "{rootdir}" not exists')
        return None
    if not is_repo_root(rootdir):
        print(f"[git_head_hash] error: {rootdir} is not a repo")
        return None

    command = ["git", "rev-parse", "HEAD"]
    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        output = subprocess.check_output(command).decode("utf-8")
        os.chdir(cwd)
        return output
    except Exception as e:
        print(f"[git_head_hash] error: {e}")
        os.chdir(cwd)
        return None


def git_config(
    rootdir: str,
    key: str,
    value: str,
    domain: Literal[
        "--global", "--system", "--local", "--worktree", "--file"
    ] = "--local",
):
    """set a configure value

    Args:
        rootdir (str): the root directory of the repository
        key (str): config option
        value (str): config value
        domain (Literal[str], optional): config file location. Defaults to "--local".
            Literal["--global", "--system", "--local", "--worktree", "--file"]

    Returns:
        bool: True if succeed

    Examples:
    ```
        # set global username:
        git_config("path/to/repo","user.name",username,"--global")
        # set global email:
        git_config("path/to/repo","user.email",email,"--global")
    ```
    """
    if not os.path.exists(rootdir):
        print(f'[git_config] error: directory "{rootdir}" not exists')
        return None
    if not is_repo_root(rootdir):
        print(f"[git_config] error: {rootdir} is not a repo")
        return None

    command = ["git", "config"]
    if domain:
        command += [domain]
    command += [key]
    command += [value]

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        subprocess.call(command)
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"[git_config] error: {e}")
        os.chdir(cwd)
        return False


def git_config_exist(
    rootdir: str,
    key: str,
    value: str,
    domain: Literal[
        "--global", "--system", "--local", "--worktree", "--file"
    ] = "--local",
):
    """check whether a config key exists or not, default search in global configure file

    Args:
        rootdir (str): the root directory of the repository
        key (str): config option
        value (str): config value
        domain (Literal[str], optional): config file location. Defaults to "--local".
            Literal["--global", "--system", "--local", "--worktree", "--file"]

    Returns:
        bool: True if exists
    """
    if not os.path.exists(rootdir):
        print(f'[git_config_exist] error: directory "{rootdir}" not exists')
        return False
    if not is_repo_root(rootdir):
        print(f"[git_config_exist] error: {rootdir} is not a repo")
        return False

    command = ["git", "config", domain, "--get-all", key]

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        result = subprocess.check_output(command).decode("utf-8").splitlines()
        if value in result:
            os.chdir(cwd)
            return True
    except Exception as e:
        print(f"[git_config_exist] error: {e}")
    os.chdir(cwd)
    return False


def git_clone(dst_dir: str, repo_url: str, rootdir: str = None):
    """clone a repository to local

    Args:
        dst_dir (str): where to store this repository, the parent dir of rootdir
        repo_url (str): url of repository
        rootdir (str, optional): rootdir of local repo. Defaults to None.
            which equals setting the rootdir with repository name

    Returns:
        bool: True if succeed
    """
    if not os.path.exists(dst_dir):
        print(
            f'[git_clone] warning: directory "{dst_dir}" not exists,'
            + " will create it automatically"
        )
        os.mkdir(dst_dir)

    command = ["git", "clone", repo_url]
    if rootdir and rootdir.strip():
        command += [rootdir]

    cwd = os.getcwd()
    try:
        os.chdir(dst_dir)
        subprocess.call(command)
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"[git_clone] error: {e}")
        os.chdir(cwd)
        return False


def git_pull(rootdir: str):
    """pull changes of remote repository

    Args:
        rootdir (str): the root directory of the repository

    Returns:
        bool: True if succeed
    """
    if not os.path.exists(rootdir):
        print(f'[git_pull] error: directory "{rootdir}" not exists')
        return False
    if not is_repo_root(rootdir):
        print(f"[git_pull] error: {rootdir} is not a repo")
        return False

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        subprocess.call(["git", "pull"])
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"[git_pull] error: {e}")
        os.chdir(cwd)
        return False


def git_remote_exist(rootdir: str, reponame: str):
    """check whether a remote url exists

    Args:
        rootdir (str): the root directory of the repository
        reponame (str): alias of remote url

    Returns:
        bool: True if exists
    """
    if not os.path.exists(rootdir):
        print(f'[git_remote_exist] error: directory "{rootdir}" not exists')
        return False
    if not is_repo_root(rootdir):
        print(f"[git_remote_exist] error: {rootdir} is not a repo")
        return False

    command = ["git", "remote", "-v"]

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        lines = subprocess.check_output(command).decode("utf-8").splitlines()
        os.chdir(cwd)
    except Exception as e:
        print(f"[git_remote_exist] error: {e}")
        os.chdir(cwd)
        return False
    for line in lines:
        if line.startswith(reponame):
            return True
    return False


def git_remote_get(rootdir: str, reponame: str):
    """get the remote url bound with an alias of the repository

    Args:
        rootdir (str): the root directory of the repository
        reponame (str): alias of remote url

    Returns:
        (str | None): remote url or None
    """
    if not os.path.exists(rootdir):
        print(f'[git_remote_get] error: directory "{rootdir}" not exists')
        return None
    if not is_repo_root(rootdir):
        print(f"[git_remote_get] error: {rootdir} is not a repo")
        return None

    command = ["git", "remote", "-v"]

    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        lines = subprocess.check_output(command).decode("utf-8").splitlines()
        os.chdir(cwd)
    except Exception as e:
        print(f"[git_remote_get] error: {e}")
        os.chdir(cwd)
        return None
    for line in lines:
        if line.startswith(reponame):
            url = line.split()[1]
            return url
    return None


def git_remote_set(rootdir: str, reponame: str, remote: str):
    """set remote url of repo, if the reponame not exists, will create it

    Args:
        rootdir (str): the root directory of the repository
        reponame (str): the alias of remote url
        remote (str): the remote url

    Returns:
        bool: True if succeed
    """
    if not os.path.exists(rootdir):
        print(f'[git_remote_set] error: directory "{rootdir}" not exists')
        return False
    if not is_repo_root(rootdir):
        print(f"[git_remote_set] error: {rootdir} is not a repo")
        return False

    cwd = os.getcwd()
    if git_remote_exist(rootdir, reponame):
        command = ["git", "remote", "set-url", reponame, remote]
        os.chdir(rootdir)
        try:
            subprocess.call(command)
            os.chdir(cwd)
            return True
        except Exception as e:
            print(f"[git_remote_set] error: {e}")
            os.chdir(cwd)
            return False
    return git_remote_add(reponame, remote)


def git_remote_add(rootdir: str, reponame: str, remote: str):
    """add a remote repository url

    Args:
        rootdir (str): the root directory of the repository
        reponame (str): the alias of remote url
        remote (str): the remote url

    Returns:
        bool: True if succeed
    """
    if not os.path.exists(rootdir):
        print(f'[git_remote_add] error: directory "{rootdir}" not exists')
        return False
    if not is_repo_root(rootdir):
        print(f"[git_remote_add] error: {rootdir} is not a repo")
        return False

    if git_remote_exist(rootdir, reponame):
        url = git_remote_get(rootdir, reponame)
        if url != remote:
            print(
                "[git_remote_add] error: there is "
                + f"already a remote url({url}) named {reponame}"
            )
            return False
        return True

    command = ["git", "remote", "add", reponame, remote]
    cwd = os.getcwd()
    try:
        os.chdir(rootdir)
        subprocess.call(command)
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"[git_remote_add] error: {e}")
        os.chdir(cwd)
        return False


if __name__ == "__main__":
    print(is_repo_root("123"))
    # print("testing git_reset_to_HEAD")
    # rootdir='test'
    # commitid="0a72079cb7f308e86a3b5c47086965140503c1e1"
    # git_reset(rootdir=rootdir,commitid="HEAD^",hard=True)
    # afterid="00b3d96"
    # beforeid="00b3d96"
    # contents=git_diff_content(rootdir="logs",beforeId=beforeid,afterId=afterid)
    # print(contents)
