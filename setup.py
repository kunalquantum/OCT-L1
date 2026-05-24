from setuptools import setup, find_packages

setup(
    name="cephmind",
    version="0.1.0",
    description="Distributed AI reasoning inspired by cephalopod cognition",
    author="CephMind Contributors",
    packages=find_packages(),
    python_requires=">=3.10",
    extras_require={
        "dev": ["pytest>=7.0"],
    },
)
