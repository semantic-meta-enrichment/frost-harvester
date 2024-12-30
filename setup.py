from setuptools import setup, find_packages

setup(
    name="frost_harvester",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "responses"
    ],
)
