from typing import List, Tuple

Literal = Tuple[str, bool]
LiteralInt = Tuple[str, bool, int]
Clause = Tuple[Literal, Literal, Literal]
ExtendedClause = List[Literal]
