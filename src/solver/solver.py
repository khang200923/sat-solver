from dataclasses import dataclass, field
from typing import Dict, List, Set
import random
from solver.types import Literal, LiteralInt, Clause, ExtendedClause
from solver.utils import li, lii, cl

@dataclass
class Solver:
    clauses: List[Clause] = field(init=False)
    assignments: Dict[Literal, int] = field(init=False)
    reasoning: Dict[LiteralInt, List[LiteralInt]] = field(init=False)
    current_decision_level: int = field(init=False)
    variables: Set[str] = field(init=False)
    satisfiable: bool | None = field(init=False)

    def __post_init__(self):
        self.reset()

    def reset(self):
        self.clauses = list()
        self.assignments = dict()
        self.reasoning = dict()
        self.current_decision_level = 0
        self.variables = set(literal[0] for clause in self.clauses for literal in clause)
        self.add_clause(cl("true true true"))
        self.satisfiable = None

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
        self.add_clause((clause[0], clause[1], li(link)))
        for literal in clause[2:-2]:
            prev_link = link
            link = f'link_{random.randint(0, 2**32)}'
            self.add_clause((li("!"+prev_link), literal, li(link)))
        self.add_clause((li("!"+link), clause[-2], clause[-1]))

    def unit_propagation(self) -> bool:
        progress = False
        for clause in self.clauses:
            # skip clauses that are already satisfied
            if set(clause) & set(self.assignments):
                continue

            skip_flag = False
            leftover: Literal | None = None
            falsifiers = []
            for literal in clause:
                neg_literal = (literal[0], not literal[1])
                if neg_literal not in self.assignments:
                    if leftover is not None and leftover != literal:
                        skip_flag = True
                        break
                    leftover = literal
                else:
                    falsifiers.append((literal[0], not literal[1], self.assignments[neg_literal]))

            if skip_flag:
                # un unitprop-able, so we skip
                continue
            if leftover is None:
                # conflict
                self.assign(li('!true'), falsifiers)
                return progress
            if leftover is not None:
                self.assign(leftover, falsifiers)
                progress = True
        return progress

    def assign(self, literal: Literal, reasoning: List[LiteralInt]):
        assert literal not in self.reasoning
        self.assignments[literal] = self.current_decision_level
        self.reasoning[literal + (self.current_decision_level,)] = reasoning

    def unassigned_variables(self) -> Set[str]:
        assigned = self.assignments
        return {
            var
            for var in self.variables
            if li(var) not in assigned and li("!" + var) not in assigned
        }

    def decision_heuristic(self) -> Literal | None:
        unassigned = tuple(self.unassigned_variables())
        if unassigned:
            return (random.choice(unassigned), bool(random.getrandbits(1)))
        return None

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
        captured_literals = [(literal[0], not literal[1]) for literal in conflict_clause]
        return max((self.assignments[literal] for literal in captured_literals if self.assignments[literal] < self.current_decision_level), default=0)

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

    def solve(self, _debug_time_limit: int | None = None) -> bool:
        clock = 0
        while True:
            clock += 1
            if _debug_time_limit is not None:
                assert clock <= _debug_time_limit
            if self.unit_propagation():
                continue
            if not self.conflict():
                decision = self.decision_heuristic()
                if decision is None:
                    self.satisfiable = True
                    break
                self.decide(decision)
                continue
            if self.current_decision_level == 0:
                self.satisfiable = False
                break
            conflict_clause = self.conflict_clause()
            self.add_extended_clause(conflict_clause)
            backjump = self.backjump_level_heuristic(conflict_clause)
            self.backjump(backjump)
        return self.satisfiable
