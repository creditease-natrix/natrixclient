#!/usr/bin/env python
# -*- coding: utf-8 -*-


import io
import os
import sys
import setuptools
import natrixclient


with io.open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

packages = [
    'natrixclient',
    'natrixclient/command',
    'natrixclient/command/check',
    'natrixclient/command/http',
    'natrixclient/command/performance',
    'natrixclient/command/ping',
    'natrixclient/common',
]

package_data = {
    "ip2region": ["natrixclient/data/*.db"]
}

install_requires = []
with open("requirements.txt", "r") as lines:
    for line in lines:
        line = line.strip()
        if len(line) and not line.startswith("#"):
            install_requires.append(line)

test_requires = []
with open("test-requirements.txt", "r") as lines:
    for line in lines:
        line = line.strip()
        if len(line) and not line.startswith("#"):
            test_requires.append(line)

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Information Technology",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Networking",
    "Topic :: Utilities",
]

setuptools.setup(
    name="natrixclient",
    version=natrixclient.version(),
    author="JamesZOU",
    author_email="zouzhicheng@foxmail.com",
    maintainer="JamesZOU",
    maintainer_email="zouzhicheng@foxmail.com",
    description="Client For Natrix - An Open Source Cloud Automation Testing Project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/creditease-natrix/natrixclient",
    download_url="https://github.com/creditease-natrix/natrixclient",
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    platforms=["RedHat", "Ubuntu", "Raspbian"],
    python_requires=">=2.7,!=3.0.*,!=3.1.*",
    install_requires=install_requires,
    tests_require=test_requires,
    scripts=["bin/natrix"],
    classifiers=classifiers,
)
