try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup

with open("Readme.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

package_data = {
    "": ["LICENSE"],
    "hotline": ["settings/defaults/*.*", "settings/user/*.*", "icons/*.*"]}

setup(
    name="hotline",
    version="0.3.1",
    description="A customizable popup input field.",
    long_description=readme,
    author="Dan Bradham",
    author_email="danielbradham@gmail.com",
    url="http://www.danbradham.com",
    packages=["hotline", "hotline.contexts"],
    package_dir={"hotline": "hotline"},
    package_data=package_data,
    include_package_data=True,
    license=license,
    zip_safe=False)
