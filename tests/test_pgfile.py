from pgsoft.pgfile import upload, download, list_files
from pgsoft.pghash.md5 import md5
import os
from datetime import datetime


def test_download():
    res = download(
        repo_id="hubei-hunan/games",
        remotepath="0462c14376e1eb03fb74f87e5a577546.json",
        repo_type="dataset",
        localdir=".",
        token=os.environ.get("db_token"),
    )
    assert isinstance(res, str)
    assert res.endswith(".json")


def test_upload():
    filename = f"{md5(datetime.now())}.json"
    res = upload(
        localpath="0462c14376e1eb03fb74f87e5a577546.json",
        remotepath=filename,
        repo_id="hubei-hunan/games",
        repo_type="dataset",
        token=os.environ.get("db_token"),
        commit_message="test commit message",
    )
    assert res


def test_list_files():
    res = list_files(
        repo_id="hubei-hunan/games",
        repo_type="dataset",
        token=os.environ.get("db_token"),
    )
    assert isinstance(res, list)
