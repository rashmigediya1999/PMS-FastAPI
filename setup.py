from setuptools import setup, find_packages

setup(
    name="payment_system",
    version="1.0.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "fastapi>=0.109.1",
        "uvicorn>=0.27.0",
        "pydantic>=2.6.1",
        "pydantic-settings>=2.1.0",
        "pymongo>=4.6.1",
        "motor>=3.3.2",
        "python-multipart>=0.0.9",
        "email-validator>=2.1.0",
        "phonenumbers>=8.13.30",
        "python-magic>=0.4.27",
        "pandas>=2.2.0",
        "PyYAML>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.8.0",
            "flake8>=7.0.0",
        ]
    },
    python_requires=">=3.8",
    description="Enterprise Payment Processing System",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
