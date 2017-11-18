#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shlex
from setuptools.command.test import test as TestCommand
from setuptools import Extension
from pip.req import parse_requirements
from tdsnmp import __version__


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

# SNMP Compilation configuration
compile_args = ['-Wno-unused-function']
snmp_base_dir = None
for arg in sys.argv:
    if arg.startswith('--debug'):
        compile_args.extend('-Wall -O0 -g'.split())
        sys.argv.remove(arg)
    elif arg.startswith('--basedir='):
        snmp_base_dir = arg.split('=')[1]
        sys.argv.remove(arg)

# Use System-provided SNMP libraries
if snmp_base_dir is None:
    netsnmp_libs = os.popen('net-snmp-config --libs').read()
    libraries = [flag[2:] for flag in shlex.split(netsnmp_libs) if flag.startswith('-l')]     # noqa
    library_dirs = [flag[2:] for flag in shlex.split(netsnmp_libs) if flag.startswith('-L')]  # noqa
    include_dirs = []
    if sys.platform == 'darwin':  # OS X
        brew = os.popen('brew info net-snmp').read()
        if 'command not found' not in brew and 'error' not in brew:
            # /usr/local/opt is the default brew `opt` prefix, however the user
            # may have installed it elsewhere. The `brew info <pkg>` includes
            # an apostrophe, which breaks shlex. We'll simply replace it
            library_dirs = [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-L')]  # noqa
            include_dirs = [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-I')]  # noqa
            # The homebrew version also depends on the Openssl keg
            brew = os.popen('brew info openssl').read()
            library_dirs += [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-L')]  # noqa
            include_dirs += [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-I')]  # noqa
# If a base directory has been provided, we use it
else:
    netsnmp_libs = os.popen('{} --libs'.format(os.path.join(snmp_base_dir, 'net-snmp-config'))).read()

    library_dirs = os.popen('{}/net-snmp-config --build-lib-dirs {}'.format(snmp_base_dir, snmp_base_dir)).read()  # noqa
    include_dirs = os.popen('{}/net-snmp-config --build-includes {}'.format(snmp_base_dir, snmp_base_dir)).read()  # noqa

    libraries = [flag[2:] for flag in shlex.split(netsnmp_libs) if flag.startswith('-l')]     # noqa
    library_dirs = [flag[2:] for flag in shlex.split(library_dirs) if flag.startswith('-L')]  # noqa
    include_dirs = [flag[2:] for flag in shlex.split(include_dirs) if flag.startswith('-I')]  # noqa

# Load requirements
base_dir = os.path.dirname(__file__)
requirements_dir = os.path.join(base_dir, 'requirements')
base_reqs = parse_requirements(os.path.join(requirements_dir, 'base.txt'), session=False)
requirements = [str(br.req) for br in base_reqs]
ci_reqs = parse_requirements(os.path.join(requirements_dir, 'ci.txt'), session=False)
test_requirements = [str(cr.req) for cr in ci_reqs]

setup(
    name='tdsnmp',
    version=__version__,
    description="TDS python package to perform SNMP commands.",
    long_description=readme + '\n\n' + history,
    author="Mark Liederbach",
    author_email='usrolh@tdstelecom.com',
    url='https://wiki.tds.net/display/admnetapps/tdsnmp',
    packages=[
        'tdsnmp',
    ],
    package_dir={'tdsnmp': 'tdsnmp'},
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    include_package_data=True,
    keywords='tdsnmp',
    ext_modules=[
        Extension(
            'tdsnmp.c.interface',['tdsnmp/c/interface.c'],
            library_dirs=library_dirs, include_dirs=include_dirs,
            libraries=libraries, extra_compile_args=compile_args
        )
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring'
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
)
