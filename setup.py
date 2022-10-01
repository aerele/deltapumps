from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in deltapumps/__init__.py
from deltapumps import __version__ as version

setup(
	name="deltapumps",
	version=version,
	description="Custom App for Delta Pumps",
	author="Delta Pumps",
	author_email="hello@aerele.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
