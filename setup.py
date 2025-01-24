from setuptools import setup, find_packages

setup(
    name="pybackendfast",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "mysql-connector-python",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "pybackendfast=app.main:app",
        ],
    },
    description="A Python FastAPI backend for Inventory, HRMS, and Accounts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://your-repository-url.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
