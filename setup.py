from setuptools import setup, find_packages


requirements = []
setup(
    name="pgsoft",
    version="v1.2.0", # do not modify
    author="PGSoft",
    license="MIT",
    url="git@github.com:east-and-west-magic/pgsoft.git",
    packages=find_packages(),
    requires=requirements,
    description="""General Python tools""",
)
