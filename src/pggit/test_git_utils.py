import pytest
import os
import subprocess
import git_utils as git


rootdir = "test"


def generate_file(filename: str, lines: list[str] = None):
    """generate a file at rootdir"""
    filepath = os.sep.join([rootdir, filename])
    with open(filepath, "w+") as f:
        if not lines:
            f.write(filepath)
        else:
            f.writelines(lines)
    return filepath


def add_all(rootdir: str):
    return subprocess.call(["git", "add", "."], cwd=rootdir)


def commit(rootdir: str, msg: str):
    return subprocess.call(["git", "commit", "-m", msg], cwd=rootdir)


def head_hash(rootdir: str):
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=rootdir
        ).decode("utf-8")
    except Exception as e:
        print(f"{e}")
        return None


def config_exist(rootdir: str, key: str, value: str):
    command = ["git", "config", "--get-all", key]
    try:
        result = (
            subprocess.check_output(command, cwd=rootdir).decode("utf-8").splitlines()
        )
        if value in result:
            return True
    except Exception as e:
        print(f"{e}")
    return False


########## Prepare test cases ##########
if git.is_repo_root(rootdir):
    while git.git_reset(rootdir):
        pass
    firstcommit = head_hash(rootdir)
else:
    if not os.path.exists(rootdir):
        os.mkdir(rootdir)
    subprocess.call(["git", "init"], cwd=rootdir)
    generate_file("README.md")
    commit(rootdir, "Initial commit")
    firstcommit = head_hash(rootdir)
initfiles = ["a.txt", "b.txt", "c.txt", "d.txt"]
for filename in initfiles:
    generate_file(filename)
    add_all(rootdir)
    commit(rootdir, filename)


@pytest.mark.parametrize(
    ["path", "result"], [(rootdir, True), ("sdfjoid", False), ("./", True)]
)
def test_is_repo_root(path: str, result: bool):
    assert git.is_repo_root(path) == result


def test_git_reset():
    res = git.git_reset(rootdir)
    hash = head_hash(rootdir)
    if res:
        assert True
    else:
        assert hash == firstcommit


def test_git_diff_content():
    filename = "git_diff_content.txt"
    lines = [f"line{i+1}\n" for i in range(100)]
    filepath = generate_file(filename, lines=lines)
    add_all(rootdir)
    commit(rootdir, filename)

    with open(filepath, "r+") as f:
        lines = f.readlines()
        lines[50] = "added line1" + "\n"
        lines[60] = "added line2" + "\n"
        lines[70] = "added line3" + "\n"
        lines.append("added line4" + "\n")
        lines.insert(80, "added line5" + "\n")
        f.seek(0)
        f.writelines(lines)

    add_all(rootdir)
    commit(rootdir, filename)
    res, added, removed = git.git_diff_content(rootdir, filename, "HEAD^", "HEAD")
    assert res
    assert added == {51: "line51", 61: "line61", 71: "line71"}
    assert removed == {
        51: "added line1",
        61: "added line2",
        71: "added line3",
        102: "added line4",
        81: "added line5",
    }


def test_git_diff_files():
    filelist = [
        "git_diff_files_modified.txt",
        "git_diff_files_deleted.txt",
    ]
    lines = [f"line{i+1}\n" for i in range(100)]
    for filename in filelist:
        generate_file(filename, lines=lines)
    add_all(rootdir)
    commit(rootdir, "git_diff_files init")
    # test add file
    generate_file("git_diff_files_added.txt")
    # test delete file
    filepath = os.sep.join([rootdir, "git_diff_files_deleted.txt"])
    os.remove(filepath)
    # test modified
    filepath = os.sep.join([rootdir, "git_diff_files_modified.txt"])
    with open(filepath, "r+") as f:
        lines = f.readlines()
        lines[50] = "added line1" + "\n"
        lines[60] = "added line2" + "\n"
        lines[70] = "added line3" + "\n"
        lines.append("added line4" + "\n")
        lines.insert(80, "added line5" + "\n")
        f.seek(0)
        f.writelines(lines)
    add_all(rootdir)
    commit(rootdir, "git_diff_files operate")

    res = git.git_diff_files(rootdir, "HEAD^", "HEAD")
    assert res is not None
    assert set(res) == {
        "git_diff_files_modified.txt",
        "git_diff_files_deleted.txt",
        "git_diff_files_added.txt",
    }
    assert res["git_diff_files_modified.txt"] == "M"
    assert res["git_diff_files_deleted.txt"] == "D"
    assert res["git_diff_files_added.txt"] == "A"


@pytest.mark.parametrize(
    ["key", "value"], [("user.name", "pytest"), ("user.email", "1234567@pytest.com")]
)
def test_git_config(key: str, value: str):
    assert git.git_config(rootdir, key, value)
    assert config_exist(rootdir, key, value)
