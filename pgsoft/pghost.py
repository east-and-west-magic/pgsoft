"""
corresponding spacenames used in the three pipelines:
- b_demo_hf: the production pipeline 1
- pgdemo2: the production pipeline 2
- pgdemo_dev: the development pipeline
"""
from gradio_client import Client


def NewClient(spacename: str, token: str):
    """Create a gradio client with the given spacename and token.

    Args:
        spacename (str): the spacename on huggingface hub, e.g. for b_demo_hf of user stevez,
        it is "stevez-b-demo-hf"
        token (str): the token of the gradio client
    """
    return Client(
        src=f"https://{spacename}.hf.space",
        hf_token=token,
        verbose=False,
    )


ais = {
    "b_demo_hf": "stevez-ai",
    "pgdemo2": "stevez-ai2",
    "pgdemo_dev": "stevez-ai-dev",
}

clouddisks = {
    "b_demo_hf": "pgsoft-clouddisk",
    "pgdemo2": "pgsoft-clouddisk",
    "pgdemo_dev": "pgsoft-clouddisk-dev",
}

clients = {
    "b_demo_hf": "stevez-b-demo-hf",
    "pgdemo2": "pgsoft-pgdemo2",
    "pgdemo_dev": "pgsoft-pgdemo-dev",
}
