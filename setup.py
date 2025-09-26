"""
Setup configuration for H1Stars Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="h1stars-payment-sdk",
    version="1.0.0",
    author="h1stars",
    author_email="predmetdev@gmail.com",
    description="Python SDK for H1Stars Payment Gateway",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h1gurodev/h1stars-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "examples": [
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
        ],
    },
    keywords="payment gateway h1stars api sdk",
    project_urls={
        "Bug Reports": "https://github.com/h1gurodev/h1stars-python-sdk/issues",
        "Source": "https://github.com/h1gurodev/h1stars-python-sdk",
        "Documentation": "https://pay.h1stars.ru/docs",
    },
)