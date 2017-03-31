import re
import sys
import shutil
from subprocess import check_call
from setuptools import setup, find_packages


if sys.argv[-1] == 'cheeseit!':
    check_call('nosetests -v')
    check_call('python setup.py sdist bdist_wheel')
    check_call('twine upload dist/*')
    shutil.rmtree('dist')
    sys.exit()
elif sys.argv[-1] == 'testit!':
    check_call('nosetests -v')
    check_call('python setup.py sdist bdist_wheel upload -r pypitest')
    sys.exit()


def get_info(pyfile):
    '''Retrieve dunder values from a pyfile'''
    info = {}
    info_re = re.compile(r"^__(\w+)__ = ['\"](.*)['\"]")
    with open(pyfile, 'r') as f:
        for line in f.readlines():
            match = info_re.search(line)
            if match:
                info[match.group(1)] = match.group(2)
    return info

info = get_info('hotline/__init__.py')

with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name=info['title'],
    version=info['version'],
    url=info['url'],
    license=info['license'],
    author=info['author'],
    author_email=info['email'],
    description=info['description'],
    long_description=long_description,
    install_requires=[],
    packages=find_packages(),
    package_data={
        'hotline': ['styles/*.*']
    },
    entry_points={},
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
