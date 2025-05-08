from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class Solver:
    clauses: List[Tuple[Tuple[int, bool], Tuple[int, bool], Tuple[int, bool]]] = field(default_factory=list)
    num_vars: int = 0
    num_clauses: int = 0
    assignments: Dict[int, bool] = field(init=False)

    def __post_init__(self):
        self.assignments = dict()

    def add_clause(self, clause: Tuple[Tuple[int, bool], Tuple[int, bool], Tuple[int, bool]]):
        self.clauses.append(clause)
        self.num_clauses += 1
        for literal in clause:
            var, _ = literal
            self.num_vars = max(self.num_vars, var + 1)

    def solve(self):
        self.assignments = dict()
        self.backtrack(0)

    def backtrack(self, level: int):
        if level > self.num_vars:
            return

        self.assignments[level] = True
        if self.is_satisfied():
            self.backtrack(level + 1)
            if level + 1 not in self.assignments:
                return

        self.assignments[level] = False
        if self.is_satisfied():
            self.backtrack(level + 1)
            if level + 1 not in self.assignments:
                return

        del self.assignments[level]

    def is_satisfied(self) -> bool:
        for clause in self.clauses:
            if not any(self.evaluate_literal(literal) for literal in clause):
                return False
        return True

    def evaluate_literal(self, literal: Tuple[int, bool]) -> bool:
        var, negated = literal
        if var not in self.assignments:
            return True
        if negated:
            return self.assignments[var] is False
        return self.assignments[var] is True
