from setuptools import setup, find_packages


requirements = ["tzdata", "python-dateutil", "gradio_client"]
setup(
    name="pgsoft",
    version="v0.1.0",  # do not modify
    author="PGSoft",
    license="MIT",
    url="git@github.com:east-and-west-magic/pgsoft.git",
    packages=find_packages(),
    requires=requirements,
    description="""General Python tools""",
)
