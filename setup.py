from setuptools import setup, find_packages

setup(
    name="cipherlab",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "streamlit",
        "pandas",
        "numpy",
        "pytest",
    ],
    entry_points={
        "console_scripts": [
            "cipherlab=app.streamlit_app:main",
        ],
    },
    python_requires=">=3.8",
)
