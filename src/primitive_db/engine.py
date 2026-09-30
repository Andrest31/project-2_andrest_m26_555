"""Command-line engine for the primitive database."""

import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db.constants import META_FILE
from src.primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from src.primitive_db.parser import parse_condition, parse_values
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Print available database commands."""
    print("\n***База данных***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> "
        "values (<значение1>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> "
        "where <столбец> = <значение> - прочитать записи"
    )
    print(
        "<command> select from <имя_таблицы> "
        "- прочитать все записи"
    )
    print(
        "<command> update <имя_таблицы> set <столбец> = "
        "<значение> where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> where "
        "<столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - информация о таблице")
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


def print_table(metadata, table_name, table_data):
    """Print table records using PrettyTable."""
    columns = metadata[table_name]
    column_names = [column[0] for column in columns]

    table = PrettyTable()
    table.field_names = column_names

    for record in table_data:
        table.add_row(
            [record.get(column_name) for column_name in column_names]
        )

    print(table)


def handle_insert(metadata, args):
    """Handle an insert command."""
    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        raise ValueError("Некорректная команда insert")

    table_name = args[2]
    values_text = " ".join(args[4:])
    values = parse_values(values_text)

    table_data = insert(metadata, table_name, values)

    if table_data is not None:
        save_table_data(table_name, table_data)


def handle_select(metadata, args):
    """Handle a select command."""
    if len(args) < 3 or args[1] != "from":
        raise ValueError("Некорректная команда select")

    table_name = args[2]

    if table_name not in metadata:
        raise KeyError(table_name)

    table_data = load_table_data(table_name)
    where_clause = None

    if len(args) > 3:
        if args[3] != "where":
            raise ValueError("Некорректная команда select")

        condition_text = " ".join(args[4:])
        where_clause = parse_condition(condition_text)

    result = select(table_data, where_clause)

    if result is not None:
        print_table(metadata, table_name, result)


def handle_update(metadata, args):
    """Handle an update command."""
    if len(args) < 8 or args[2] != "set":
        raise ValueError("Некорректная команда update")

    table_name = args[1]

    if table_name not in metadata:
        raise KeyError(table_name)

    if "where" not in args:
        raise ValueError("В команде update отсутствует where")

    where_index = args.index("where")

    set_text = " ".join(args[3:where_index])
    where_text = " ".join(args[where_index + 1:])

    set_clause = parse_condition(set_text)
    where_clause = parse_condition(where_text)

    table_data = load_table_data(table_name)

    result = update(
        table_data,
        set_clause,
        where_clause,
    )

    if result is None:
        return

    updated_data, updated_ids = result

    save_table_data(table_name, updated_data)

    for record_id in updated_ids:
        print(
            f"Запись с ID={record_id} в таблице "
            f'"{table_name}" успешно обновлена.'
        )


def handle_delete(metadata, args):
    """Handle a delete command."""
    if len(args) < 6 or args[1] != "from":
        raise ValueError("Некорректная команда delete")

    table_name = args[2]

    if table_name not in metadata:
        raise KeyError(table_name)

    if args[3] != "where":
        raise ValueError("В команде delete отсутствует where")

    where_text = " ".join(args[4:])
    where_clause = parse_condition(where_text)

    table_data = load_table_data(table_name)

    result = delete(
        table_data,
        where_clause,
    )

    if result is None:
        return

    updated_data, deleted_ids = result

    save_table_data(table_name, updated_data)

    for record_id in deleted_ids:
        print(
            f"Запись с ID={record_id} успешно удалена "
            f'из таблицы "{table_name}".'
        )


def handle_info(metadata, args):
    """Print information about a table."""
    if len(args) != 2:
        raise ValueError("Некорректная команда info")

    table_name = args[1]

    if table_name not in metadata:
        raise KeyError(table_name)

    columns = metadata[table_name]
    table_data = load_table_data(table_name)

    columns_text = ", ".join(
        f"{name}:{data_type}"
        for name, data_type in columns
    )

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_text}")
    print(f"Количество записей: {len(table_data)}")


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

        try:
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
                    raise ValueError("create_table")

                table_name = args[1]
                columns = parse_columns(args[2:])

                old_metadata = metadata.copy()
                result = create_table(
                    metadata,
                    table_name,
                    columns,
                )

                if result is not None and result != old_metadata:
                    save_metadata(META_FILE, result)

            elif command == "drop_table":
                if len(args) != 2:
                    raise ValueError("drop_table")

                old_metadata = metadata.copy()
                result = drop_table(metadata, args[1])

                if result is not None and result != old_metadata:
                    save_metadata(META_FILE, result)

            elif command == "insert":
                handle_insert(metadata, args)

            elif command == "select":
                handle_select(metadata, args)

            elif command == "update":
                handle_update(metadata, args)

            elif command == "delete":
                handle_delete(metadata, args)

            elif command == "info":
                handle_info(metadata, args)

            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except KeyError as error:
            print(f"Ошибка: Таблица {error} не существует.")
        except ValueError as error:
            print(
                f"Некорректное значение: {error}. "
                "Попробуйте снова."
            )