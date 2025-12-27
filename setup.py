from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="buildtovalue",
    version="0.9.0",
    author="BuildToValue Contributors",
    author_email="dev@buildtovalue.com",
    description="Enterprise AI Governance Framework with ISO 42001 Compliance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/buildtovalue/btv-framework",
    project_urls={
        "Bug Tracker": "https://github.com/buildtovalue/btv-framework/issues",
        "Documentation": "https://docs.buildtovalue.ai",
        "Source Code": "https://github.com/buildtovalue/btv-framework",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.23",
        "pyyaml>=6.0.1",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "btv-server=src.interface.api.gateway:main",
            "btv-token=scripts.generate_token:main",
        ],
    },
)
