import pytest
from solver import Solver
from solver.utils import li, cl

@pytest.mark.repeat(5)
def test_solve_0():
    solver = Solver()
    solver.add_clause(cl("a !true !true"))
    solver.add_clause(cl("b !a !true"))
    assert solver.solve(10)
    assert solver.assignments == {li('true'): 0, li('a'): 0, li('b'): 0}

@pytest.mark.repeat(5)
def test_solve_1():
    solver = Solver()
    solver.add_clause(cl("!a !true !true"))
    solver.add_clause(cl("b a !true"))
    solver.add_clause(cl("a !b !c"))
    assert solver.solve(10)
    assert solver.assignments == {li('true'): 0, li('!a'): 0, li('b'): 0, li('!c'): 0}

@pytest.mark.repeat(5)
def test_solve_2():
    solver = Solver()
    solver.add_clause(cl("!a b !true"))
    solver.add_clause(cl("!a c !true"))
    solver.add_clause(cl("!b !c !true"))
    assert solver.solve(20)
    assert solver.assignments.keys() in [
        {li('true'), li('!a'), li('!b'), li('c')},
        {li('true'), li('!a'), li('b'), li('!c')},
        {li('true'), li('!a'), li('!b'), li('!c')}
    ]
