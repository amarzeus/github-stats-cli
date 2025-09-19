from setuptools import setup, find_packages

setup(
    name="github-stats-cli",
    version="0.1.0",
    py_modules=['github_stats_cli'],
    entry_points={
        'console_scripts': [
            'github-stats=github_stats_cli:main',
        ],
    },
    install_requires=[
        'requests',
    ],
    author="Amar Kumar",
    description="A CLI tool to fetch GitHub user statistics",
    url="https://github.com/amarzeus/github-stats-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
