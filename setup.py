import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ProcessRunner",
    version="0.0.1",
    author="Sam Bland",
    author_email="sbland.co.uk@gmail.com",
    description="Functional Process Runner",
    setup_requires=[
        'pytest-cov',
        'pytest-runner',
        'numpy',
    ],
    tests_require=['pytest'],
    extras_require={'test': ['pytest']},
    packages=setuptools.find_packages(),
    package_dir={'src': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
)
