#!/usr/bin/python
import codecs
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


setup(
    name="LeIA",
    packages=find_packages(),
    include_package_data=True,
    version="0.0.26",
    description="LeIA (Léxico para Inferência Adaptada) é um fork do léxico e ferramenta para análise de sentimentos VADER (Valence Aware Dictionary and sEntiment Reasoner) adaptado para textos em português, com suporte para emojis e foco na análise de sentimentos de textos expressos em mídias sociais - mas funcional para textos de outros domínios.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="rfjaa",
    author_email="rafjaa@gmail.com",
    url="https://github.com/rafjaa/LeIA",
    install_requires=["requests"],
    keywords=[
        "vader",
        "sentiment",
        "analysis",
        "opinion",
        "mining",
        "nlp",
        "text",
        "data",
        "text analysis",
        "opinion analysis",
        "sentiment analysis",
        "text mining",
        "twitter sentiment",
        "opinion mining",
        "social media",
        "twitter",
        "social",
        "media",
        "portuguese",
        "brazilian",
        "brazilian portuguese",
    ],
    classifiers=[
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: General",
    ],
)
