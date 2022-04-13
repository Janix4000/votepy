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
    author="Jan Izydorczyk, Filip Nikolow, Mateusz Słuszniak",
    author_email="unexpected@sent.at",
    description="A Python library of ordinal-based committee (OBC) voting rules",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Janix4000/votepy/",
    project_urls={"Bug Tracker": "https://github.com/Janix4000/votepy/issues"},
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    packages=["votepy"],
    python_requires=">=3.8",
    setup_requires=[
        "wheel",
    ],
    install_requires=[
        "numpy>=1.20",
    ],
    extras_require={
        "dev": [
            "pytest>=6",
            "coverage[toml]>=5.3",
            "matplotlib>=3.4.3",
        ]
    },
)