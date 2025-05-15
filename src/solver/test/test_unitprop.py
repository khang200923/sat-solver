import pytest
from solver import Solver
from solver.utils import li, cl

def repeated_unitprop(solver: Solver):
    while True:
        res = solver.unit_propagation()
        if not res:
            break

@pytest.mark.repeat(5)
def test_unitprop_0():
    solver = Solver()
    repeated_unitprop(solver)
    assert solver.assignments == {li('true'): 0}

@pytest.mark.repeat(5)
def test_unitprop_1():
    solver = Solver()
    solver.add_clause(cl("a !true !true"))
    solver.add_clause(cl("b !a !true"))
    repeated_unitprop(solver)
    assert solver.assignments == {li('true'): 0, li('a'): 0, li('b'): 0}

@pytest.mark.repeat(5)
def test_unitprop_2():
    solver = Solver()
    solver.add_clause(cl("!a !true !true"))
    solver.add_clause(cl("b a !true"))
    repeated_unitprop(solver)
    assert solver.assignments == {li('true'): 0, li('!a'): 0, li('b'): 0}

@pytest.mark.repeat(5)
def test_unitprop_3():
    solver = Solver()
    solver.add_clause(cl("!a !true !true"))
    solver.add_clause(cl("b a !true"))
    solver.add_clause(cl("a !b !c"))
    repeated_unitprop(solver)
    assert solver.assignments == {li('true'): 0, li('!a'): 0, li('b'): 0, li('!c'): 0}

@pytest.mark.repeat(5)
def test_unitprop_4():
    solver = Solver()
    solver.add_clause(cl("a !true !true"))
    solver.add_clause(cl("!a !true !true"))
    repeated_unitprop(solver)
    assert solver.conflict()
