"""Command-line engine for the primitive database."""

import shlex

import prompt

from src.primitive_db.constants import META_FILE
from src.primitive_db.core import create_table, drop_table
from src.primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Print available database commands."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_columns(column_args):
    """Parse column definitions from command arguments."""
    columns = []

    for column in column_args:
        if ":" not in column:
            raise ValueError(column)

        name, data_type = column.split(":", 1)
        columns.append((name, data_type))

    return columns


def run():
    """Run the main database command loop."""
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string("Введите команду: ")
        args = shlex.split(user_input)

        if not args:
            continue

        command = args[0]

        if command == "exit":
            break

        if command == "help":
            print_help()

        elif command == "list_tables":
            if not metadata:
                print("Таблицы отсутствуют.")
            else:
                for table_name in metadata:
                    print(f"- {table_name}")

        elif command == "create_table":
            if len(args) < 3:
                print("Некорректное значение. Попробуйте снова.")
                continue

            table_name = args[1]

            try:
                columns = parse_columns(args[2:])
            except ValueError as error:
                print(
                    f"Некорректное значение: {error}. "
                    "Попробуйте снова."
                )
                continue

            old_metadata = metadata.copy()
            metadata = create_table(metadata, table_name, columns)

            if metadata != old_metadata:
                save_metadata(META_FILE, metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение. Попробуйте снова.")
                continue

            old_metadata = metadata.copy()
            metadata = drop_table(metadata, args[1])

            if metadata != old_metadata:
                save_metadata(META_FILE, metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")