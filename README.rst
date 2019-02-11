Et_module (energy_transport_module)
====================================
.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: http://et-module.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/nismod/et_module.svg?branch=master
    :target: https://travis-ci.org/nismod/et_module

.. image:: https://coveralls.io/repos/github/nismod/et_module/badge.svg?branch=master
    :target: https://coveralls.io/github/nismod/et_module?branch=master


Temporally diasaggregates energy demand output from transport model.

The hourly electricity demand is used to simulate the V2G and G2V capacity based on
simplified assumptions about average electric vehicle battery capacity and assumptions
on average states of charges. The simulated capacity can then be used by the energy supply
model in its optimisation.

.. image:: https://github.com/nismod/et_module/blob/master/docs/_images/002_capacity_modelling.jpg
    :alt: Et_module overview
    :width: 60%
    :align: center
