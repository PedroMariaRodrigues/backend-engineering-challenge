from setuptools import setup

setup(
    name="unbabel-cli",
    version="0.1.0",
    description="Event processing pipeline with configurable metrics",
    author="Pedro Rodrigues",
    author_email="pedro.maria.rodrigues@tecnico.ulisboa.pt",
    py_modules=["unbabel_cli", "event", "process", "read", "write", "metrics_"],
    package_dir={"": "src"}, 
    install_requires=[],  # Move the to requirements.txt
    entry_points={
        "console_scripts": [
            "unbabel_cli = unbabel_cli:main",
        ],
    },
    python_requires=">=3.8",
)