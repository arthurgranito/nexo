import pytest
from app.sql_guard import validate_query
S = "t_00000000000000000000000000000010"

def test_scoped_select():
    result = validate_query(f"select sum(total) from {S}.vendas", S, {"vendas"})
    assert "LIMIT 500" in result

def test_preserves_smaller_limit():
    result = validate_query(f"select * from {S}.vendas limit 10", S, {"vendas"})
    assert "LIMIT 10" in result

@pytest.mark.parametrize("sql", [
    "delete from vendas", "select * from public.users", "select * from vendas",
    f"select * from {S}.vendas; drop table vendas",
    f"select pg_sleep(10) from {S}.vendas",
    f"select * into x from {S}.vendas",
    f"select * from {S}.vendas for update",
    f"with x as (delete from {S}.vendas returning *) select * from x",
    f"select * from {S}.vendas limit 10000",
])
def test_rejects_unsafe_sql(sql):
    with pytest.raises(ValueError):
        validate_query(sql, S, {"vendas"})
