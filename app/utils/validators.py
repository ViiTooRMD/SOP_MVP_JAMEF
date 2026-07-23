def missing_columns(columns, required):
    available = set(columns)
    return [column for column in required if column not in available]
