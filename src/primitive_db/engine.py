import prompt


def welcome():
    """Prints welcome message and handles basic help/exit commands"""

    print("Первая попытка запустить проект!")
    print("***")
    print("<command> exit   выйти из программы")
    print("<command> help   справочная информация")

    while True:
        cmd = prompt.string("Введите команду: ").strip()

        if cmd == "exit":
            break
        elif cmd == "help":
            print("<command> exit   выйти из программы")
            print("<command> help   справочная информация")
        elif cmd == "":
            continue
        else:
            print(f"Команды {cmd} нет. Попробуйте снова.")