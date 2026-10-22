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
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Prints the help message for the current mode."""
    print("\n*** Доступные команды ***")
    print("create_table <name> <col:type> ... - создать таблицу")
    print("list_tables                       - список таблиц")
    print("drop_table <name>                 - удалить таблицу")
    print("insert into <name> values (...)   - добавить запись")
    print("select from <name> [where ...]    - выбрать записи")
    print("update <name> set c=v where c=v   - обновить записи")
    print("delete from <name> where c=v      - удалить записи")
    print("exit                              - выход")
    print("help                              - справка\n")


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
                metadata = create_table(metadata, args[1], args[2:])
                save_metadata(META_FILE, metadata)
            elif cmd == "drop_table":
                if len(args) < 2:
                    print("Ошибка: укажите имя таблицы.")
                    continue
                metadata = drop_table(metadata, args[1])
                save_metadata(META_FILE, metadata)
            elif cmd == "insert" and len(args) > 2 and args[1] == "into":
                table_name = args[2]
                # Ожидаем формат: insert into users values val1 val2 ...
                if "values" not in args:
                    print("Ошибка: пропущено ключевое слово values.")
                    continue
                val_index = args.index("values")
                raw_vals = args[val_index + 1 :]
                
                table_data = load_table_data(table_name)
                table_data = insert_record(metadata, table_name, table_data, raw_vals)
                save_table_data(table_name, table_data)
            elif cmd == "select" and len(args) > 2 and args[1] == "from":
                table_name = args[2]
                table_data = load_table_data(table_name)
                
                where_clause = None
                if "where" in args:
                    w_index = args.index("where")
                    where_clause = " ".join(args[w_index + 1 :])

                filtered = select_records(table_data, where_clause)
                
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
                table_data = update_records(table_data, set_clause, where_clause)
                save_table_data(table_name, table_data)
            elif cmd == "delete" and args[1] == "from":
                # delete from users where ID=1
                table_name = args[2]
                where_idx = args.index("where")
                where_clause = " ".join(args[where_idx + 1 :])

                table_data = load_table_data(table_name)
                table_data = delete_records(table_data, where_clause)
                save_table_data(table_name, table_data)
            else:
                print(f"Функции {cmd} нет. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка выполнения: {e}")