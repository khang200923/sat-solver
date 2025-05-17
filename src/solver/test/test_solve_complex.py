import random
from typing import List, Tuple
import pytest
from solver.solver import Solver
from solver.types import Literal
from solver.utils import li

def int_to_bool_list(n: int, bit_length: int | None = None) -> List[bool]:
    # (creds to chatgpt)
    if bit_length is None:
        # Use minimal bits required to represent the number
        bit_length = n.bit_length() or 1  # at least 1 bit for zero
    binary_str = format(n, f'0{bit_length}b')  # binary string padded with leading zeros
    return [bit == '1' for bit in binary_str]

def sample_one_solution_sat(solution: List[bool]) -> Tuple[List[List[Literal]], List[Literal]]:
    res = range(2**len(solution))
    res = [int_to_bool_list(num, len(solution)) for num in res]
    res.remove(solution)
    res = [[(f"x{i}", not xx) for i, xx in enumerate(x)] for x in res]
    aaa = [(f"x{i}", xx) for i, xx in enumerate(solution)]
    return res, aaa

def one_solution_sats(num: int, length: int) -> List[Tuple[List[List[Literal]], List[Literal]]]:
    return [sample_one_solution_sat(int_to_bool_list(random.randrange(2**length), length)) for _ in range(num)]

def add_extended_clauses(solver: Solver, ecs: List[List[Literal]]):
    for ec in ecs:
        solver.add_extended_clause(ec)

@pytest.mark.parametrize('problem,solution', one_solution_sats(10, 3))
def test_one_solution_sats_3(problem: List[List[Literal]], solution: List[Literal]):
    solver = Solver()
    add_extended_clauses(solver, problem)
    assert solver.solve(1000)
    assert set(solver.assignments.keys()) == {li('true'), *solution}

@pytest.mark.parametrize('problem,solution', one_solution_sats(10, 4))
def test_one_solution_sats_4(problem: List[List[Literal]], solution: List[Literal]):
    solver = Solver()
    add_extended_clauses(solver, problem)
    assert solver.solve(1000)
    result = set(solver.assignments.keys())
    result = {x for x in result if not x[0].startswith('link_')}
    assert result == {li('true'), *solution}

@pytest.mark.parametrize('problem,solution', one_solution_sats(10, 5))
def test_one_solution_sats_5(problem: List[List[Literal]], solution: List[Literal]):
    solver = Solver()
    add_extended_clauses(solver, problem)
    assert solver.solve(10000)
    result = set(solver.assignments.keys())
    result = {x for x in result if not x[0].startswith('link_')}
    assert result == {li('true'), *solution}
