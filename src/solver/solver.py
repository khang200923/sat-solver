from dataclasses import dataclass, field
from typing import Dict, List, Set
import random
from solver.types import Literal, LiteralInt, Clause, ExtendedClause
from solver.utils import li, lii, cl, ec

@dataclass
class Solver:
    clauses: List[Clause] = field(init=False)
    assignments: Dict[Literal, int] = field(init=False)
    reasoning: Dict[LiteralInt, List[LiteralInt]] = field(init=False)
    current_decision_level: int = field(init=False)
    variables: Set[str] = field(init=False)
    solved: bool | None = field(init=False)

    def __post_init__(self):
        self.reset()

    def reset(self):
        self.clauses = list()
        self.assignments = dict()
        self.reasoning = dict()
        self.current_decision_level = 0
        self.variables = set(literal[0] for clause in self.clauses for literal in clause)
        self.add_clause(cl("true true true"))
        self.solved = None

    def add_clause(self, clause: Clause):
        self.clauses.append(clause)
        self.variables.update(literal[0] for literal in clause)

    def add_extended_clause(self, clause: ExtendedClause):
        if len(clause) == 0:
            return
        if len(clause) == 1:
            self.add_clause((clause[0], li('!true'), li('!true')))
            return
        if len(clause) == 2:
            self.add_clause((clause[0], clause[1], li('!true')))
            return
        if len(clause) == 3:
            self.add_clause((clause[0], clause[1], clause[2]))
            return
        link: str = f'link_{random.randint(0, 2**32)}'
        prev_link: str = ""
        self.add_clause((clause[0], clause[1], li(link)))
        for literal in clause[2:-2]:
            prev_link = link
            link = f'link_{random.randint(0, 2**32)}'
            self.add_clause((li("!"+prev_link), literal, li(link)))
        self.add_clause((li("!"+prev_link), clause[-2], clause[-1]))

    def unit_propagation(self) -> bool:
        progress = False
        for clause in self.clauses:
            if any(literal in self.assignments for literal in clause):
                continue
            leftovers = set(literal for literal in clause if (literal[0], not literal[1]) not in self.assignments)
            falsifiers = set((literal[0], not literal[1], self.assignments[(literal[0], not literal[1])]) for literal in clause if (literal[0], not literal[1]) in self.assignments)
            if len(leftovers) == 0:
                # conflict
                self.assign(li('!true'), list(falsifiers))
                return True
            if len(leftovers) == 1:
                self.assign(list(leftovers)[0], list(falsifiers))
                progress = True
        return progress

    def assign(self, literal: Literal, reasoning: List[LiteralInt]):
        assert literal not in self.reasoning
        self.assignments[literal] = self.current_decision_level
        self.reasoning[literal + (self.current_decision_level,)] = reasoning

    def unassigned_variables(self) -> Set[str]:
        return {variable for variable in self.variables if li(variable) not in self.assignments and li('!' + variable) not in self.assignments}

    def decision_heuristic(self) -> Literal:
        # just use a random literal whatever
        return (random.sample(self.unassigned_variables(), 1)[0], random.choice((True, False)))

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

    def backjump_level_heuristic(self, conflict_clause: ExtendedClause) -> int:
        return max((self.assignments[literal] for literal in conflict_clause if self.assignments[literal] < self.current_decision_level), default=0)

    def decide(self, literal: Literal):
        if literal in self.assignments:
            raise ValueError(f"Literal {literal} already assigned")
        self.current_decision_level += 1
        self.assign(literal, [])

    def backjump(self, level: int):
        if level >= self.current_decision_level:
            raise ValueError(f"Level {level} is not less than current decision level {self.current_decision_level}")
        self.current_decision_level = level
        for literal in list(self.assignments.keys()):
            if self.assignments[literal] > level:
                del self.assignments[literal]
        for literal in list(self.reasoning.keys()):
            if literal[2] > level:
                del self.reasoning[literal]
