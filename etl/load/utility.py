from sqlalchemy.dialects.postgresql import insert


def upsert_on_conflict_do_nothing(table, conn, keys, data_iter):
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data).on_conflict_do_nothing()
    result = conn.execute(stmt)
    return result.rowcount
