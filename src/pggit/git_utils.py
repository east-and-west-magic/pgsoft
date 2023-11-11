"""a module implemented with subprocess module,
providing some tools to manage repository
"""

import os
import subprocess
from typing_extensions import Self, Sequence, Literal, Union
import re


def is_repo_root(path: str):
    """check if the path is a root directory of a repository

    Args:
        path (str): a existed path

    Returns:
        bool: True if it's a repo
    """
    if not os.path.exists(path):
        print(f'[is_repo_root] error: directory "{path}" not exists')
        return False

    command = ["git", "-C", path, "rev-parse", "--show-toplevel"]
    try:
        rootdir = subprocess.check_output(command).decode("utf-8").strip("\n")
        if os.path.samefile(rootdir, path):
            return True
    except Exception as e:
        print(f"[is_repo_root] error: {e}")
    return False


class Repo:
    def __init__(self, rootdir: str):
        """local repository manager, interacting with
            remote(i.e. pull or push) is not included

        Args:
            rootdir (str): the root directory of a repository

        Returns:
            Repo | None: normally return Repo object,
                return None if the rootdir is not a repo
        """
        self.rootdir = rootdir

    def __new__(cls, rootdir: str) -> Self:
        if not is_repo_root(rootdir):
            print(f"[git_add] error: {rootdir} is not a repo")
            return None
        return super().__new__(cls)

    def git_add(self, files: str | Sequence[str] = "."):
        """stage the changes in these files since last stage

        Args:
            files (str | Sequence[str], optional): a single file or
                a list of files to be added. Defaults to ".", which means adding all.

        Returns:
            bool: True if succeed
        """
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

        try:
            subprocess.call(command, cwd=self.rootdir)
            return True
        except Exception as e:
            print(f"[git_add] error: {e}")
            return False

    def git_reset_hard(self, commitid: str = "HEAD"):
        """forcely reset the repository to an committed version.

        Args:
            commitid (str, optional): a valid commit id. Defaults to "HEAD".
        Returns:
            bool: succeed or not
        """
        try:
            # track and stage all
            command = ["git", "add", "."]
            subprocess.call(command, cwd=self.rootdir)
            command = ["git", "reset", "--hard", commitid]
            subprocess.call(command, cwd=self.rootdir)
            return True
        except Exception as e:
            print(f"[git_reset] error: {e}")
            return False

    def git_diff_file(self, filepath: str, beforeId: str, afterId: str):
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
        command = ["git", "diff", beforeId, afterId, filepath]
        try:
            res = subprocess.check_output(command, cwd=self.rootdir).decode("utf-8")
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

    def git_diff_all(self, beforeId: str, afterId: str, nameonly: bool = True):
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
        command = ["git", "diff"]
        if nameonly:
            command += ["--name-only"]
        command += [beforeId, afterId]

        try:
            res = subprocess.check_output(command, cwd=self.rootdir).decode("utf-8")
            res = res.replace("/", os.sep).splitlines()
        except Exception as e:
            print(f"[git_diff] error: {e}")
            return None
        if nameonly:
            outp = res
        else:
            outp = {}
            for filepath in res:
                outp[filepath] = self.git_diff_file(filepath, beforeId, afterId)
        return outp

    def get_head_hash(self):
        """get the commit id of HEAD pointer"""
        command = ["git", "rev-parse", "HEAD"]
        try:
            output = subprocess.check_output(command, cwd=self.rootdir).decode("utf-8")
            return output
        except Exception as e:
            print(f"[git_head_hash] error: {e}")
            return None

    def git_config(
        self,
        key: str,
        value: str,
        domain: Literal[
            "--global", "--system", "--local", "--worktree", "--file"
        ] = "--local",
    ):
        """set a configure value

        Args:
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
        command = ["git", "config"]
        if domain:
            command += [domain]
        command += [key]
        command += [value]

        try:
            subprocess.call(command, cwd=self.rootdir)
            return True
        except Exception as e:
            print(f"[git_config] error: {e}")
            return False
