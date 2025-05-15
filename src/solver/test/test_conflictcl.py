import pytest
from solver import Solver
from solver.utils import li, cl
from solver.test.test_unitprop import repeated_unitprop

@pytest.mark.repeat(5)
def test_conflict_0():
    solver = Solver()
    solver.add_clause(cl("!a b !true"))
    solver.add_clause(cl("!a c !true"))
    solver.add_clause(cl("!b !c !true"))
    repeated_unitprop(solver)
    assert solver.assignments == {li('true'): 0}
    solver.decide(li('a'))
    repeated_unitprop(solver)
    assert solver.conflict()
    assert set(solver.conflict_clause()) == {li('!a'), li('!true')}

@pytest.mark.repeat(5)
def test_conflict_1():
    solver = Solver()
    solver.add_clause(cl("a !true !true"))
    solver.add_clause(cl("!true !true !a"))
    repeated_unitprop(solver)
    assert solver.conflict()
    assert set(solver.conflict_clause()) == {li('!true')}

@pytest.mark.repeat(5)
def test_conflict_2():
    solver = Solver()
    solver.add_clause(cl("!true !true !true"))
    repeated_unitprop(solver)
    assert solver.conflict()
    assert set(solver.conflict_clause()) == {li('!true')}

@pytest.mark.repeat(5)
def test_conflict_3():
    # credits to https://www.cs.princeton.edu/courses/archive/fall13/cos402/readings/SAT_learning_clauses.pdf
    solver = Solver()
    solver.add_clause(cl("x1 x2 !true"))
    solver.add_clause(cl("x1 x3 x7"))
    solver.add_clause(cl("!x2 !x3 x4"))
    solver.add_clause(cl("!x4 x5 x8"))
    solver.add_clause(cl("!x4 x6 x9"))
    solver.add_clause(cl("!x5 !x6 !true"))
    repeated_unitprop(solver)
    assert solver.assignments == {li('true'): 0}
    solver.decide(li('!x7'))
    repeated_unitprop(solver)
    assert not solver.conflict()
    solver.decide(li('!x8'))
    repeated_unitprop(solver)
    assert not solver.conflict()
    solver.decide(li('!x9'))
    repeated_unitprop(solver)
    assert not solver.conflict()
    solver.decide(li('!x1'))
    repeated_unitprop(solver)
    assert solver.conflict()
    assert set(solver.conflict_clause()) == {li('!x4'), li('x8'), li('x9'), li('!true')}
