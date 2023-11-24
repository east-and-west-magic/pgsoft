from setuptools import setup, find_packages


requirements = []
setup(
    name="pgsoft",
    version="1.0",
    author="Beracles",
    license="MIT",
    url="git@github.com:east-and-west-magic/pgsoft.git",
    packages=find_packages(),
    requires=requirements,
    description="""a package of some general tools for python developing""",
)
