from setuptools import setup, find_packages

setup(
    name="truthmark-sdk",
    version="1.0.0",
    description="Developer SDK for TruthMark - Easy integration for AI watermarking",
    author="Round Tech",
    packages=find_packages(),
    install_requires=[
        "truthmark-core>=1.0.0",
        "numpy",
        "opencv-python"
    ],
    python_requires=">=3.8",
)
