__author__="gmcwhirt"
__date__ ="$Sep 26, 2011 2:43:53 PM$"

from setuptools import setup, find_packages

setup (
  name = 'gametheory.deception',
  version = '0.0.1',
  packages = find_packages('src'),
  package_dir = {
    '': 'src',
  },
  namespace_packages = ['gametheory'],
  author = 'Gregory McWhirter',
  author_email = 'gmcwhirt@uci.edu',
  description = 'Game theory simulations for deception research',
  url = 'https://www.github.com/gsmcwhirter/gametheory',
  license = 'MIT',
  entry_points = {
    "console_scripts": [
        "gt.deception.replicator.sim = gametheory.deception.replicator.simulations:run",
        "gt.deception.replicator.stats = gametheory.deception.replicator.stats:run",
        "gt.deception.learning.sim = gametheory.deception.learning.main:run",
        "gt.deception.learning.stats = gametheory.deception.learning.stats:run",
        "gt.deception.replicator_comp.sim = gametheory.deception.replicator_comparison.simulations:run",
        "gt.deception.replicator_comp.stats = gametheory.deception.replicator_comparison.stats:run",
    ]
  }
)
