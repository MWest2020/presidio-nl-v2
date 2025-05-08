from setuptools import setup, find_packages

setup(
    name="presidio-nl",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "presidio-analyzer",
        "spacy",
        "click",
        # Voeg hier andere requirements toe indien nodig
    ]
) 