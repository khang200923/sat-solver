from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
import random

Literal = Tuple[str, bool]
LiteralInt = Tuple[str, bool, int]
Clause = Tuple[Literal, Literal, Literal]
ExtendedClause = List[Literal]

@dataclass
class Solver:
    clauses: List[Clause] = field(default_factory=list)
    unsolved_clauses: Set[int] = field(default_factory=set)
    assignments: Dict[Literal, int] = field(init=False)
    unassigned_variables: Set[str] = field(init=False)
    reasoning: Dict[LiteralInt, List[LiteralInt]] = field(init=False)
    current_decision_level: int = field(init=False)

    def __post_init__(self):
        self.unassigned_variables = set(literal[0] for clause in self.clauses for literal in clause)
        self.assignments = dict()
        self.reasoning = dict()
        self.current_decision_level = 0
        self.add_clause((
            ("true", True), ("true", True), ("true", True)
        ))

    def add_clause(self, clause: Clause):
        self.clauses.append(clause)
        self.unsolved_clauses.add(len(self.clauses) - 1)
        self.unassigned_variables.update(literal[0] for literal in clause)

    def unit_propagation(self) -> bool:
        progress = False
        for i in self.unsolved_clauses.copy():
            clause = self.clauses[i]
            leftovers = set(literal for literal in clause if (literal[0], not literal[1]) not in self.assignments)
            falsifiers = set((literal[0], not literal[1], self.assignments[(literal[0], not literal[1])]) for literal in clause if (literal[0], not literal[1]) in self.assignments)
            assert len(leftovers) > 0
            if len(leftovers) == 1:
                self.assign(list(leftovers)[0], list(falsifiers))
                self.unsolved_clauses.remove(i)
                progress = True
        return progress

    def assign(self, literal: Literal, reasoning: List[LiteralInt]):
        assert literal not in self.reasoning
        self.assignments[literal] = self.current_decision_level
        self.reasoning[literal + (self.current_decision_level,)] = reasoning
        self.unassigned_variables.discard(literal[0])

    def decision_heuristic(self) -> Literal:
        # just use a random literal whatever
        return (random.sample(self.unassigned_variables, 1)[0], random.choice((True, False)))

    def conflict(self) -> str | None:
        conflicty = [literal[0] for literal in self.assignments if (literal[0], not literal[1]) in self.assignments]
        assert len(conflicty) <= 1
        if conflicty:
            return conflicty[0]
        return
