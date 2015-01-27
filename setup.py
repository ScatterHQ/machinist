#!/usr/bin/env python
# Copyright Hybrid Logic Ltd.  See LICENSE file for details.

from inspect import cleandoc

from setuptools import setup

import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'machinist/_version.py'
versioneer.versionfile_build = 'machinist/_version.py'
versioneer.tag_prefix = 'machinist-' # tags are like 1.2.0
versioneer.parentdir_prefix = 'machinist-' # dirname like 'machinist-1.2.0'


# For the convenience of the travis configuration, make this information
# particularly easy to find.  See .travis.yml.
_MINIMUM_ELIOT_VERSION = "0.5.0"

if __name__ == '__main__':
    setup(
        name="machinist",
        version=versioneer.get_version(),
        # Allow versioneer to integrate with setup commands:
        cmdclass=versioneer.get_cmdclass(),
        packages=["machinist", "machinist.test"],
        description=cleandoc("""
            Machinist is a tool for building finite state machines.
        """),
        long_description=cleandoc("""
            A finite state machine maps simple, symbolic inputs to simple, symbolic
            outputs.  In this context, symbolic means that nothing differentiates
            the values from each other apart from their identity.

            The mapping from inputs to outputs also includes definitions for state
            transitions.  The current state of the machine changes to a new value
            each time an input is mapped to an output (though the new value may be
            the same as the old value).
            """),
        url="https://github.com/ClusterHQ/machinist",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",

            # General classifiers to indicate "this project supports Python 2" and
            # "this project supports Python 3".
            "Programming Language :: Python :: 2",

            # More specific classifiers to indicate more precisely which versions
            # of those languages the project supports.
            "Programming Language :: Python :: 2.7",

            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",

            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        install_requires=[
            "zope.interface>=3.6.0", "twisted>=13.1",
            ],
        extras_require={
            "dev": ["sphinx>=1.2.2"],
            "logging": ["eliot>=" + _MINIMUM_ELIOT_VERSION],
            },
        test_suite="machinist",
        )
