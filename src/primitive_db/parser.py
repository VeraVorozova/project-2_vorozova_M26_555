def parse_values(values_args: list[str], schema: dict) -> list:
    """Validate and convert the provided values.

    The values are cast to match the column types specified in the schema.
    """
    # schema содержит ключи вроде {'ID': 'int', 'name': 'str', 'age': 'int', ...}
    col_items = list(schema.items())[1:]
    
    if len(values_args) != len(col_items):
        raise ValueError(
            f"Неверное количество аргументов. " 
            f"Ожидается {len(col_items)}, получено {len(values_args)}."
        )

    parsed_values = []
    for (col_name, col_type), val_str in zip(col_items, values_args):
        if col_type == "int":
            try:
                parsed_values.append(int(val_str))
            except ValueError:
                raise ValueError(
                    f"Некорректное значение для '{col_name}': ожидалось int."
                )
        elif col_type == "bool":
            if val_str.lower() in ("true", "1", "yes"):
                parsed_values.append(True)
            elif val_str.lower() in ("false", "0", "no"):
                parsed_values.append(False)
            else:
                raise ValueError(
                    f"Некорректное значение для '{col_name}': ожидалось bool."
                )
        elif col_type == "str":
            parsed_values.append(str(val_str))
        else:
            parsed_values.append(val_str)

    return parsed_values


def parse_condition(condition_str: str) -> tuple[str, any]:
    """Parses a condition of the form column = value into a (column, value) pair."""
    if "=" not in condition_str:
        raise ValueError(f"Некорректное условие: {condition_str}")
    
    col, val = condition_str.split("=", 1)
    col = col.strip()
    val = val.strip()

    # Приводим к нужному типу
    if val.isdigit():
        val = int(val)
    elif val.lower() == "true":
        val = True
    elif val.lower() == "false":
        val = False
    elif ((val.startswith('"') and val.endswith('"')) or 
          (val.startswith("'") and val.endswith("'"))):
        val = val[1:-1]

    return col, val