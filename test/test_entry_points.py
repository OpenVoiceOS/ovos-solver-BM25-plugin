# Licensed under the Apache License, Version 2.0
"""Every declared entry point must load the class it names.

`ovos-evidence-solver-bm25` named `BM25SolverPlugin`, a class this package does
not define; the class is `BM25EvidenceSolverPlugin`. Nothing caught it, because
the metadata carries the name whether or not the attribute exists, and the
group `opm.solver.reading_comprehension` was empty in practice: loading the
entry point raised `AttributeError`.

This reads the installed distribution's own metadata rather than a list written
here, so a future entry point is covered the day it is added.
"""
import importlib.metadata as md

import pytest

DISTRIBUTION = "ovos-solver-bm25-plugin"

EXPECTED_BASES = {
    "opm.solver.question": "QuestionSolver",
    "opm.solver.summarization": "TldrSolver",
    "opm.solver.reading_comprehension": "EvidenceSolver",
    "opm.solver.multiple_choice": "MultipleChoiceSolver",
}


def _declared():
    """Yield (group, name, value) for every entry point this package ships."""
    eps = md.distribution(DISTRIBUTION).entry_points
    return [(ep.group, ep.name, ep.value) for ep in eps]


def test_the_package_declares_entry_points():
    """A guard on the guard: an empty list would pass every row below."""
    assert len(_declared()) == 5, _declared()


@pytest.mark.parametrize("group,name,value", _declared())
def test_entry_point_loads(group, name, value):
    """Loading must return the class the entry point names."""
    ep = next(e for e in md.distribution(DISTRIBUTION).entry_points
              if e.group == group and e.name == name)
    obj = ep.load()  # raises AttributeError when the class does not exist
    assert isinstance(obj, type), f"{name} loaded {obj!r}, not a class"
    assert obj.__name__ == value.split(":")[1]


@pytest.mark.parametrize("group,name,value", _declared())
def test_entry_point_subclasses_its_group_base(group, name, value):
    """The class must be the kind of solver its group promises.

    A name can load and still be the wrong class, which is how the evidence
    entry point could have been pointed at any other solver in the module and
    still pass a load test.
    """
    ep = next(e for e in md.distribution(DISTRIBUTION).entry_points
              if e.group == group and e.name == name)
    base_name = EXPECTED_BASES[group]
    bases = [b.__name__ for b in ep.load().__mro__]
    assert base_name in bases, \
        f"{name} is a {bases[0]}, which is not a {base_name}"
