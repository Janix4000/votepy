import os
import setuptools
import subprocess


def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        readme = fh.read()
    return readme


def read_version() -> str:
    return '0.0.1'


setuptools.setup(
    name="votepy",
    version=read_version(),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Janix4000/votepy/",
    project_urls={"Bug Tracker": "https://github.com/Janix4000/votepy/issues"},
    packages=['votepy', 'votepy.rules', 'votepy.algorithms', 'votepy.meta'],
)
