"""
The setup.py file contains info about pakaging the project
"""

from typing import List

from setuptools import find_packages, setup


def get_requirements() -> List[str]:
    """
    This function will return list of requirements
    """
    requirement_lst: List[str] = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                # ignore empty lines and -e .
                if requirement and requirement != "-e .":
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_lst


setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Pranav Tupe",
    author_email="pranavtupe2512@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)
