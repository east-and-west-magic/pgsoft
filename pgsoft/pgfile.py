from huggingface_hub import HfApi
import os

api = HfApi()


def upload(
    localpath: str,
    remotepath: str,
    repo_id: str,
    repo_type: str,
    token: str,
    commit_message: str = None,
) -> bool:
    """upload file to repository on huggingface hub

    Args:
        localpath (str): full local path of the file, e.g. /home/user/file.txt
        remotepath (str): destination path in the repository, e.g. file.txt
        repo_id (str): repository id, e.g. username/reponame
        repo_type (str): type of repository, dataset, space, or model
        token (str): huggingface hub api token
        commit_message (str): message for the commit

    Returns:
        str: url of the uploaded file
    """
    try:
        res = api.upload_file(
            path_or_fileobj=localpath,
            path_in_repo=remotepath,
            repo_id=repo_id,
            repo_type=repo_type,
            token=token,
            commit_message=commit_message,
            run_as_future=False,
        )
        print(f"uploaded to {res}")
        return True
    except Exception as e:
        print(f"{type(e)}: {e}")
        return False


def download(
    repo_id: str,
    remotepath: str,
    repo_type: str,
    localdir: str,
    token: str,
) -> str | None:
    """download file from repository on huggingface hub

    Args:
        repo_id (str): repository id, e.g. username/reponame
        remotepath (str): path of file in the repository, e.g. file.txt
        repo_type (str): type of repository, dataset, space, or model
        localdir (str): local directory to save the file to
        token (str): huggingface hub api token

    Returns:
        str: full local path of the file
    """
    filename = os.path.basename(remotepath)
    subfolder = os.path.dirname(remotepath)
    try:
        localpath = api.hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type=repo_type,
            local_dir=localdir,
            token=token,
            subfolder=subfolder,
        )
        print(f"downloaded to {localpath}")
        return localpath
    except Exception as e:
        print(f"{type(e)}: {e}")
        return None


def list_files(
    repo_id: str,
    repo_type: str,
    token: str,
) -> list | None:
    """list files in a repository on huggingface hub

    Args:
        repo_id (str): repository id, e.g. username/reponame
        repo_type (str): type of repository, dataset, space, or model
        token (str): huggingface hub api token
    """
    try:
        res = api.list_repo_files(
            repo_id=repo_id,
            repo_type=repo_type,
            token=token,
        )
        return res
    except Exception as e:
        print(f"{type(e)}: {e}")
        return None
