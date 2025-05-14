from solver.types import Literal, LiteralInt, Clause, ExtendedClause
import re

def format_literal(literal: str) -> Literal:
    if literal.startswith("!"):
        return (literal[1:], False)
    else:
        return (literal, True)
li = format_literal

def format_literal_int(literal: str | Literal, level: int | None = None) -> LiteralInt:
    if isinstance(literal, tuple):
        if level is None:
            raise ValueError("LiteralInt must have a level")
        return (*literal, level)
    if level is None:
        res = re.match(r"^(.*?):([0-9]+)$", literal)
        if res:
            return (*li(res.group(1)), int(res.group(2)))
        raise ValueError(f"Invalid literal format: {literal}")
    return (*li(literal), level)
lii = format_literal_int

def format_clause(clause: str) -> Clause:
    literals = clause.split(" ")
    if len(literals) != 3:
        raise ValueError(f"Invalid clause format: {clause}")
    return (li(literals[0]), li(literals[1]), li(literals[2]))
cl = format_clause

def format_extended_clause(clause: str) -> ExtendedClause:
    literals = clause.split(" ")
    return [li(literal) for literal in literals]
ec = format_extended_clause
