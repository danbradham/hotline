try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import sys
import hotline


if sys.argv[-1] == 'cheeseit!':
    os.system('python setup.py sdist upload')
    sys.exit()
elif sys.argv[-1] == 'cheeseit':
    os.system('python setup.py sdist upload -r pypitest')
    sys.exit()


packages = [
    'hotline',
    'hotline.contexts',
    'hotline.ui'
]

package_data = {
    '': ['LICENSE', 'README.rst'],
    'hotline': ['conf/*.*']
}


with open('README.rst') as f:
    readme = f.read()


setup(
    name='hotline',
    version=hotline.__version__,
    description=hotline.__description__,
    long_description=readme,
    author=hotline.__author__,
    author_email=hotline.__email__,
    url=hotline.__url__,
    license=hotline.__license__,
    packages=packages,
    package_data=package_data,
    package_dir={'hotline': 'hotline'},
    include_package_data=True,
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
    install_requires=(
        "PySide",
    ),
)
