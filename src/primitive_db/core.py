from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.parser import parse_condition, parse_values
from primitive_db.utils import delete_table_file


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
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
            print(f"Некорректный тип данных '{col_type}'.")
            return metadata
        parsed_columns.append((col_name, col_type))

    metadata[table_name] = {name: dtype for name, dtype in parsed_columns}
    print(f'Таблица "{table_name}" успешно создана.')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Remove a table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    
    del metadata[table_name]
    delete_table_file(table_name)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
def list_tables(metadata: dict) -> None:
    """Lists all existing tables."""
    if not metadata:
        print("Таблиц пока нет.")
        return
    
    for name in metadata:
        print(name)


@handle_db_errors
@log_time
def insert_record(
        metadata: dict, 
        table_name: str, 
        table_data: list[dict], 
        raw_values: list[str]
    ) -> list[dict]:
    """Adds a new record with an automatically generated ID."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    schema = metadata[table_name]
    values = parse_values(raw_values, schema)

    # Генерация ID (максимальный ID + 1 или 1, если таблица пуста)
    new_id = max((row["ID"] for row in table_data), default=0) + 1

    new_record = {"ID": new_id}
    col_names = list(schema.keys())[1:]
    for col, val in zip(col_names, values):
        new_record[col] = val

    table_data.append(new_record)
    print(f"Запись с ID={new_id} успешно добавлена в таблицу \"{table_name}\".")
    return table_data


@handle_db_errors
@log_time
def select_records(
        table_data: list[dict], 
        where_clause: str | None = None
    ) -> list[dict]:
    """Selects records, with the option to filter using a `WHERE` clause."""
    if not where_clause:
        return table_data

    col, val = parse_condition(where_clause)
    filtered = [row for row in table_data if row.get(col) == val]
    return filtered


@handle_db_errors
def update_records(
        table_data: list[dict], set_clause: str, 
        where_clause: str
    ) -> list[dict]:
    """Updates records based on a WHERE condition."""
    set_col, set_val = parse_condition(set_clause)
    where_col, where_val = parse_condition(where_clause)

    updated_count = 0
    for row in table_data:
        if row.get(where_col) == where_val:
            row[set_col] = set_val
            updated_count += 1

    print(f"Обновлено записей: {updated_count}.")
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete_records(table_data: list[dict], where_clause: str) -> list[dict]:
    """Deletes records based on a WHERE condition."""
    where_col, where_val = parse_condition(where_clause)
    
    initial_len = len(table_data)
    table_data = [row for row in table_data if row.get(where_col) != where_val]
    deleted_count = initial_len - len(table_data)

    print(f"Успешно удалено записей: {deleted_count}.")
    return table_data


@handle_db_errors
def info_table(metadata: dict, table_name: str, table_data: list[dict]) -> None:
    """Displays information about a table (its structure and the number of records)."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    
    schema = metadata[table_name]
    cols_str = ", ".join(f"{name}:{dtype}" for name, dtype in schema.items())
    
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(table_data)}")