import shlex

import prompt

from primitive_db.constants import META_FILE
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Prints help message."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> ... — создать таблицу")
    print("<command> list_tables — показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> — удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit — выход из программы")
    print("<command> help — справочная информация\n")


def run():
    """Main interactive loop."""
    print("***База данных***")
    print_help()

    while True:
        try:
            user_input = prompt.string(">>>Введите команду: ").strip()
        except (KeyboardInterrupt,  EOFError):
            break

        if not user_input:
            continue
        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга команды: {e}")
            continue

        cmd = args[0]
        metadata = load_metadata(META_FILE)

        if cmd == "exit":
            break
        elif cmd == "help":
            print_help()
        elif cmd == "list_tables":
            list_tables(metadata)
        elif cmd == "create_table":
            if len(args) < 2:
                print("Ошибка: Укажите имя таблицы.")
                continue
            table_name = args[1]
            columns = args[2:]
            metadata = create_table(metadata, table_name, columns)
            save_metadata(META_FILE, metadata)
        elif cmd == "drop_table":
            if len(args) < 2:
                print("Ошибка: Укажите имя таблицы.")
                continue
            table_name = args[1]
            metadata = drop_table(metadata, table_name)
            save_metadata(META_FILE, metadata)
        else:
            print(f"Функции {cmd} нет. Попробуйте снова.")