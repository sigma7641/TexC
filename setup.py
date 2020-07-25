from setuptools import setup, find_packages
with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()
setup(
    name="TexC",
    version="0.0.1",
    description="A small package",
    author="sigma7641",
    packages=find_packages(),
    install_requires=install_requirements,
    entry_points={
        "console_scripts": [
            "TexC=TexC.core:main",
        ]
    }
    )