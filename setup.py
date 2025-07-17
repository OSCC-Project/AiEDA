from setuptools import setup, find_packages
import os
from pathlib import Path

def get_version():
    init_file = Path(__file__).parent / "aieda" / "__init__.py"
    print(f"Looking for version in {init_file}")
    if init_file.exists():
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"\'')
    return "0.1.0"

def get_long_description():
    readme_file = Path(__file__).parent / "README.md"
    print(f"Looking for long description in {readme_file}")
    if readme_file.exists():
        return readme_file.read_text(encoding="utf-8")
    return "AI-Enhanced Electronic Design Automation Library with iEDA Integration"

def get_requirements():
    requirements_file = Path(__file__).parent / "requirements.txt"
    print(f"Looking for requirements in {requirements_file}")
    if requirements_file.exists():
        with open(requirements_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    # default requirements
    return [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "pyyaml>=5.4.0",
        "click>=8.0.0",
        "tqdm>=4.60.0",
    ]

setup(
    name="aieda",
    version=get_version(),
    author="yhqiu",
    author_email="qiuyihang23@mails.ucas.ac.cn",
    description="AI-Enhanced Electronic Design Automation Library with iEDA Integration",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/ieda-iai/aieda_fork",
    
    packages=find_packages(),
    
    # include ieda_py
    package_data={
        'aieda.third_party.iEDA.bin': ['*.so'],
    },
    include_package_data=True,
    
    python_requires=">=3.8",
    install_requires=get_requirements(),
    
    extras_require={
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research", 
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    keywords="eda, ieda, vlsi, place-and-route, ai",
)