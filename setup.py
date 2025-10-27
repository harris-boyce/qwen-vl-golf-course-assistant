from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="qwen-vl-golf-assistant",
    version="0.1.0",
    author="Harris Boyce",
    description="AI agent for golf course analysis using Qwen-VL, satellite imagery, and web scraping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harris-boyce/qwen-vl-golf-course-assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "golf-assistant=golf_assistant.cli:main",
        ],
    },
)
