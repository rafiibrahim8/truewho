from setuptools import setup, find_packages
from truewho import __version__


def read_file(filename, lines=False):
    try:
        with open(filename, "r") as f:
            if lines:
                return [i.strip() for i in f.readlines() if (i.strip())]
            return f.read()
    except:
        print("Can not read file:", filename)
        return None


long_description = read_file("README.md")

setup(
    name="truewho",
    version=__version__,
    author="Ibrahim Rafi",
    author_email="me@ibrahimrafi.me",
    license="MIT",
    url="https://github.com/rafiibrahim8/truewho",
    download_url="https://github.com/rafiibrahim8/truewho/archive/v{}.tar.gz".format(
        __version__
    ),
    install_requires=["phone-iso3166", "requests", "click"],
    description="Check a phone number for name with Truecaller in command line.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["truewho", "Truecaller", "Spam", "Call"],
    packages=find_packages(),
    entry_points=dict(console_scripts=["truewho=truewho.truewho:main"]),
    platforms=["any"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
