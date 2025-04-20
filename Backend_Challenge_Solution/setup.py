from setuptools import setup, find_packages

setup(
    name="unbabel-cli",
    version="0.1.0",
    py_modules=["unbabel_cli"],
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.0",
    ],
    entry_points={
        "console_scripts": [
            "unbabel_cli = unbabel_cli:main",
        ],
    },
)