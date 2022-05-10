import setuptools
import pathlib
import sys

if sys.version_info < (3, 10):
    raise RuntimeError('aiowallhaven requires Python 3.6 or greater')

_ROOT = pathlib.Path(__file__).parent

with open(str(_ROOT / 'README.md')) as f:
    readme = f.read()

setuptools.setup(
        name="aiowallhaven",
        version="0.0.1",
        author="Dmitrii Efimov",
        author_email="efimov.1992@outlook.com",
        description="Async wrapper for Wallhaven's API",
        long_description=readme,
        long_description_content_type="text/markdown",
        url="https://github.com/itsuchur/aiowallhaven",
        download_url = 'https://github.com/itsuchur/aiowallhaven/archive/refs/tags/0.0.2.tar.gz',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.10',
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
        python_requires='>=3.10.0',
        license='MIT',
        )