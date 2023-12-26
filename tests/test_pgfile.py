from pgsoft.pgfile import upload, download, list_files
from pgsoft.pghash.md5 import md5
import os
from glob import glob
from datetime import datetime


testcontent = """
{
    "device-id": "test_device", 
    "meta-data": {}, 
    "game-file": 
    {
        "user_gold_info":[
            {
                "ID": 1001, 
                "Name": "Snake", 
                "PicPath": "res://Src/images/Bird/NoBg/bird_1.png", 
                "Key": ""
            }]
    }
}"""
jsonlist = glob("*.json")
for item in jsonlist:
    os.remove(item)
filename = f"test_{md5(datetime.now())}.json"
with open(filename, "w") as f:
    f.write(testcontent)


def test_upload():
    res = upload(
        localpath=filename,
        remotepath=filename,
        repo_id="hubei-hunan/games",
        repo_type="dataset",
        token=os.environ.get("db_token"),
        commit_message="test uploading",
    )
    assert res


def test_download():
    res = download(
        repo_id="hubei-hunan/games",
        remotepath=filename,
        repo_type="dataset",
        localdir=".",
        token=os.environ.get("db_token"),
    )
    assert isinstance(res, str)
    assert res.endswith(filename)
    with open(res, "r") as f:
        assert f.read() == testcontent


def test_list_files():
    res = list_files(
        repo_id="hubei-hunan/games",
        repo_type="dataset",
        token=os.environ.get("db_token"),
    )
    assert isinstance(res, list)
    assert filename in res
