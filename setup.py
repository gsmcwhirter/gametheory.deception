#!/usr/bin/env python

from distutils.core import setup

setup (
    name = 'gametheory.deception',
    version = '0.1',
    packages = [
        "gametheory.deception.replicator",
        "gametheory.deception.replicator_comparison"
    ],
    package_dir = {
        '': 'src',
    },
    requires = ["gametheory.base >= 0.1"],
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
