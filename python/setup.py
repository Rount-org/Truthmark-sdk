from setuptools import setup, find_packages

setup(
    name="truthmark-sdk",
    version="1.0.0",
    description="Developer SDK for TruthMark - Easy integration for AI watermarking",
    author="Rount",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "opencv-python"
    ],
    python_requires=">=3.8",
)
