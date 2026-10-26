import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import (
    create_table,
    delete_records,
    drop_table,
    insert_record,
    list_tables,
    select_records,
    update_records,
    info_table,
)
from primitive_db.decorators import create_cacher
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

query_cacher = create_cacher()

def print_help():
    """Prints the help message for the current mode."""

    table_commands = [
        (
            "<command> create_table <имя_таблицы> "
            "<столбец1:тип> <столбец2:тип> ..",
            "- создать таблицу",
        ),
        ("<command> list_tables ", "- показать список всех таблиц"),
        ("<command> drop_table <имя_таблицы> ", "- удалить таблицу"),
        (
            "<command> insert into <имя_таблицы> "
            "values (<значение1>, <значение2>, ...)",
            "- создать запись.",
        ),
        (
            "<command> select from <имя_таблицы> "
            "where <столбец> = <значение>",
            "- прочитать записи по условию.",
        ),
        ("<command> select from <имя_таблицы> ", "- прочитать все записи."),
        (
            "<command> update <имя_таблицы> "
            "set <столбец1> = <новое_значение1> "
            "where <столбец_условия> = <значение_условия>",
            "- обновить запись.",
        ),
        (
            "<command> delete from <имя_таблицы> "
            "where <столбец> = <значение>",
            "- удалить запись.",
        ),
        (
            "<command> info <имя_таблицы>",
            "- вывести информацию о таблице.",
        ),
    ]
    common_commands = [
        "<command> exit - выход из программы",
        "<command> help - справочная информация",
    ]

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("\n".join(f"{cmd} {desc}" for cmd, desc in table_commands))

    print("\nОбщие команды:")
    print("\n".join(common_commands))
    print()


def run():
    """Main interactive loop."""
    print("*** Примитивная база данных ***")
    print_help()

    while True:
        try:
            user_input = prompt.string(">>> Введите команду: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            continue

        metadata = load_metadata(META_FILE)
        cmd = args[0] if args else ""

        try:
            if cmd == "exit":
                break
            elif cmd == "help":
                print_help()
            elif cmd == "list_tables":
                list_tables(metadata)
            elif cmd == "create_table":
                if len(args) < 2:
                    print("Ошибка: укажите имя таблицы.")
                    continue
                table_name = args[1]
                metadata = create_table(metadata, args[1], args[2:])
                save_metadata(META_FILE, metadata)
                save_table_data(table_name, [])
            elif cmd == "drop_table":
                if len(args) < 2:
                    print("Ошибка: укажите имя таблицы.")
                    continue
                metadata = drop_table(metadata, args[1])
                save_metadata(META_FILE, metadata)
                query_cacher(invalidate_table=table_name)
            elif cmd == "insert" and len(args) > 2 and args[1] == "into":
                table_name = args[2]
                # Ожидаем формат: insert into users values val1 val2 ...
                if "values" not in args:
                    print("Ошибка: пропущено ключевое слово values.")
                    continue
                val_index = args.index("values")
                raw_vals = args[val_index + 1 :]
                
                table_data = load_table_data(table_name)
                updated_data = insert_record(metadata, table_name, table_data, raw_vals)
                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                    query_cacher(invalidate_table=table_name)
            elif cmd == "select" and len(args) > 2 and args[1] == "from":
                table_name = args[2]
                table_data = load_table_data(table_name)
                
                where_clause = None
                if "where" in args:
                    w_index = args.index("where")
                    where_clause = " ".join(args[w_index + 1 :])
                cache_key = (table_name, where_clause)
                filtered = query_cacher(
                    cache_key,
                    lambda: select_records(table_data, where_clause)
                ) 
                
                # Вывод через PrettyTable
                if filtered and table_name in metadata:
                    table = PrettyTable()
                    table.field_names = list(metadata[table_name].keys())
                    for row in filtered:
                        table.add_row([row.get(col) for col in table.field_names])
                    print(table)
                else:
                    print("Записи не найдены.")
            elif cmd == "update":
                # update users set age=29 where name="Sergei"
                table_name = args[1]
                set_idx = args.index("set")
                where_idx = args.index("where")
                
                set_clause = " ".join(args[set_idx + 1 : where_idx])
                where_clause = " ".join(args[where_idx + 1 :])

                table_data = load_table_data(table_name)
                updated_data = update_records(table_data, set_clause, where_clause)
                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                    query_cacher(invalidate_table=table_name)
            elif cmd == "delete" and args[1] == "from":
                # delete from users where ID=1
                table_name = args[2]
                where_idx = args.index("where")
                where_clause = " ".join(args[where_idx + 1 :])

                table_data = load_table_data(table_name)
                updated_data = delete_records(table_data, where_clause)
                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                    query_cacher(invalidate_table=table_name)
            elif cmd == "info" and len(args) > 1:
                table_name = args[1]
                table_data = load_table_data(table_name)
                info_table(metadata, table_name, table_data)

            else:
                print(f"Функции {cmd} нет. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка выполнения: {e}")