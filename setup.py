#!/usr/bin/env python

import os
from importlib.util import module_from_spec, spec_from_file_location

from pkg_resources import parse_requirements
from setuptools import find_packages, setup

_PATH_ROOT = os.path.dirname(__file__)


def _load_py_module(fname, pkg="slack_command_bot"):
    spec = spec_from_file_location(
        os.path.join(pkg, fname), os.path.join(_PATH_ROOT, pkg, fname)
    )
    py = module_from_spec(spec)
    spec.loader.exec_module(py)
    return py


def _load_requirements(path_dir: str, file_name: str = "requirements.txt") -> list:
    reqs = parse_requirements(open(os.path.join(path_dir, file_name)).readlines())
    return list(map(str, reqs))


# https://packaging.python.org/discussions/install-requires-vs-requirements /
# keep the meta-data here for simplicity in reading this file... it's not obvious
# what happens and to non-engineers they won't know to look in init ...
# the goal of the project is simplicity for researchers, don't want to add too much
# engineer specific practices


setup(
    name="slack_command_bot",
    version="0.1.0",
    description="⚡ With this app you can create a Slack bot and enable interactivity with the Slash Commands.",
    author="Aniket Maurya",
    author_email="aniket@lightning.ai",
    url="https://github.com/Lightning-AI/LAI-slack-slash-command-bot-Component",
    download_url="https://github.com/Lightning-AI/LAI-slack-slash-command-bot-Component",
    packages=find_packages(exclude=["tests", "docs"]),
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
    keywords=["deep learning", "pytorch", "AI"],
    python_requires=">=3.7",
    setup_requires=["wheel"],
    install_requires=_load_requirements(_PATH_ROOT),
)
