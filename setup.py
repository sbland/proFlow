import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proflow",
    version="0.4.7",
    author="Sam Bland",
    author_email="sbland.co.uk@gmail.com",
    description="Functional Process Runner",
    setup_requires=[
        'pytest-cov',
        'pytest-runner',
        'numpy',
        'scipy',
        'ipycanvas'
    ],
    tests_require=['pytest', 'snapshottest'],
    extras_require={'test': ['pytest']},
    packages=setuptools.find_packages(),
    package_dir={'proflow': 'proflow', 'vendor': 'vendor'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
