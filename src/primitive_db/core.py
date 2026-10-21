from primitive_db.constants import VALID_TYPES


def create_table(metadata:  dict, table_name: str, columns: list[str]) -> dict:
    """Creates a new table schema with automatically prepended ID:int column."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = [("ID", "int")]

    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        col_name, col_type = col.split(":", 1)

        if col_type not in VALID_TYPES:
            print(
                f"Некорректный тип данных '{col_type}'."
                f"Поддерживаются: {', '.join(VALID_TYPES)}"
            )
            return metadata
        parsed_columns.append((col_name, col_type))

    metadata[table_name] = {
        name: dtype for name, dtype in parsed_columns
    }
    cols_str = ", ".join(f"{name}:{dtype}" for name, dtype in parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Remove a table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata:dict) -> None:
    """Lists all existing tables."""
    if not metadata:
        print("Таблиц пока нет.")
        return
    
    for name in metadata:
        print(name)