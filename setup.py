from setuptools import setup, find_packages


setup(
    name="pgsoft",
    version="v0.1.0",  # do not modify
    author="PGSoft",
    license="MIT",
    url="git@github.com:east-and-west-magic/pgsoft.git",
    packages=find_packages(),
    install_requires = [
        "gradio_client",
        "python-dateutil", 
        "huggingface_hub",
        "tzdata", 
    ],
    description="A Python library used by our backend development",
)
