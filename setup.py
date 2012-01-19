#!/usr/bin/env python

from setuptools import setup

setup (
    name = 'gametheory.deception',
    version = '0.2.0',
    packages = [
        "gametheory.deception",
        "gametheory.deception.replicator",
        "gametheory.deception.replicator_comparison"
    ],
    package_dir = {
        '': 'src',
    },
    install_requires = [
        'distribute',
        'gametheory.base (>=0.3.0)'
    ],
    dependency_links = ["https://www.ideafreemonoid.org/pip"],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    author = 'Gregory McWhirter',
    author_email = 'gmcwhirt@uci.edu',
    description = 'Game theory simulations for deception research',
    url = 'https://www.github.com/gsmcwhirter/gametheory',
    license = 'MIT',
    scripts = [
        "scripts/gt.deception.replicator.sim",
        "scripts/gt.deception.replicator.stats",
        "scripts/gt.deception.replicator_comp.sim",
        "scripts/gt.deception.replicator_comp.stats"
    ]
)
