import re
import sqlglot
from sqlglot import exp

def validate_query(sql: str, schema: str, tables: set[str]) -> str:
    """Defense in depth; executor also needs a restricted PG role + read-only transaction."""
    if not re.fullmatch(r"t_[0-9a-f]{32}", schema):
        raise ValueError("Schema inválido")
    statements = sqlglot.parse(sql, read="postgres")
    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError("Somente um SELECT simples é permitido nesta versão")
    tree = statements[0]
    allowed_functions = {"SUM", "COUNT", "AVG", "MIN", "MAX", "COALESCE", "ROUND", "CAST"}
    if tree.args.get("into") or tree.args.get("locks") or tree.args.get("with_"):
        raise ValueError("INTO, locks e CTE não habilitados")
    if any(isinstance(node, (exp.Subquery, exp.Union)) for node in tree.walk()):
        raise ValueError("Subqueries e unions não habilitados")
    for fn in tree.find_all(exp.Func):
        if fn.sql_name() not in allowed_functions:
            raise ValueError("Função não permitida")
    found = list(tree.find_all(exp.Table))
    if not found:
        raise ValueError("Consulta deve ler uma tabela autorizada")
    for table in found:
        if table.catalog or table.db != schema or table.name not in tables:
            raise ValueError("Tabela fora do catálogo autorizado")
    limit = tree.args.get("limit")
    if limit is not None:
        raw = limit.expression
        if not isinstance(raw, exp.Literal) or not raw.is_int or not 1 <= int(raw.this) <= 500:
            raise ValueError("LIMIT deve ser inteiro entre 1 e 500")
    row_limit = int(limit.expression.this) if limit is not None else 500
    return tree.limit(row_limit, copy=False).sql(dialect="postgres")
