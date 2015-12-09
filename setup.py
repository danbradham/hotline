from setuptools import setup, find_packages
import os
import sys
import hotline


if sys.argv[-1] == 'cheeseit!':
    os.system('python setup.py sdist upload')
    sys.exit()
elif sys.argv[-1] == 'testit!':
    os.system('python setup.py sdist upload -r pypitest')
    sys.exit()


with open('README.rst') as f:
    readme = f.read()


setup(
    name=hotline.__title__,
    version=hotline.__version__,
    description=hotline.__description__,
    long_description=readme,
    author=hotline.__author__,
    author_email=hotline.__email__,
    url=hotline.__url__,
    license=hotline.__license__,
    package_data={
        '': ['LICENSE', 'README.rst'],
        'hotline': ['conf/*.*', 'ui/style.css'],
    },
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
    ),
)
