from dataclasses import dataclass, field
from typing import Dict, List, Set
import random
from solver.types import Literal, LiteralInt, Clause, ExtendedClause
from solver.utils import li, lii, cl, ec

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
        self.add_clause(cl("true true true"))

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
            if len(leftovers) == 0:
                # conflict
                self.assign(li('!true'), list(falsifiers))
                self.unsolved_clauses.remove(i)
                return True
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

    def conflict(self) -> bool:
        return li('!true') in self.assignments

    def conflict_clause(self) -> ExtendedClause:
        if not self.conflict():
            raise ValueError("No conflict")
        current_level = self.current_decision_level
        leftovers: Set[Literal] = {li('!true')}
        assert lii('!true', current_level) in self.reasoning
        lowers: Set[Literal] = set()
        for element in reversed(self.reasoning):
            if len(leftovers) <= 1 and li('!true') not in leftovers:
                break
            if element[2] != current_level:
                continue
            element = element[:2]
            if element not in leftovers:
                continue
            leftovers.discard(element)
            assert lii(element, current_level) in self.reasoning
            if not self.reasoning[lii(element, current_level)]:
                # wow a decision literal
                leftovers = {element}
                break
            for causes in self.reasoning[lii(element, current_level)]:
                if causes[2] == current_level:
                    leftovers.add(causes[:2])
                else:
                    lowers.add(causes[:2])
        return list((literal[0], not literal[1]) for literal in lowers | leftovers)

    def decide(self, literal: Literal):
        if literal in self.assignments:
            raise ValueError(f"Literal {literal} already assigned")
        self.current_decision_level += 1
        self.assign(literal, [])
