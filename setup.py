from setuptools import setup, find_packages

setup(
    name='Rufus',
    version='1.0.0',
    description='A tool for intelligent web data extraction and synthesis for RAG systems',
    author='Shreyans Jain',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'beautifulsoup4',
        'sentence_transformers',
    ],
)
