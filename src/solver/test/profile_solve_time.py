import cProfile
import pstats
import random
from typing import List, Tuple
import pytest
from solver.solver import Solver
from solver.types import Literal
from solver.utils import li
from solver.test.test_solve_complex import int_to_bool_list, sample_one_solution_sat, one_solution_sats, add_extended_clauses

def main():
    solver = Solver()
    for i, (problem, solution) in enumerate(one_solution_sats(2000, 4)):
        solver.reset()
        add_extended_clauses(solver, problem)
        try:
            assert solver.solve(1000000)
        except AssertionError:
            print("too much:", i)
            continue
        result = set(solver.assignments.keys())
        result = {x for x in result if not x[0].startswith('link_')}
        assert result == {li('true'), *solution}

if __name__ == "__main__":
    cProfile.run('main()', 'log')
    p = pstats.Stats('log')
    p.sort_stats('cumtime').print_stats(20)
