from setuptools import setup, find_packages

setup(
    name="webaudit",
    version="1.0.0",
    description="Website Reconnaissance and Security Auditing Toolkit",
    author="Your Name",
    python_requires=">=3.12",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
        "rich>=13.7.0",
        "jinja2>=3.1.0",
        "pandas>=2.2.0",
        "validators>=0.22.0",
    ],
    entry_points={
        "console_scripts": [
            "webaudit=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
        "Intended Audience :: Education",
    ],
)
