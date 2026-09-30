"""Core database operations."""

from src.primitive_db.constants import VALID_TYPES
from src.primitive_db.decorators import (
    confirm_action,
    handle_db_errors,
    log_time,
)
from src.primitive_db.utils import load_table_data


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Create a new table in database metadata."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    for column_name, column_type in columns:
        if column_type not in VALID_TYPES:
            print(f"Некорректное значение: {column_type}. Попробуйте снова.")
            return metadata

    table_columns = [("ID", "int")] + columns
    metadata[table_name] = table_columns

    columns_text = ", ".join(
        f"{name}:{data_type}" for name, data_type in table_columns
    )

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_text}"
    )

    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Delete a table from database metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Insert a new record into a table."""
    if table_name not in metadata:
        raise KeyError(table_name)

    columns = metadata[table_name]
    data_columns = columns[1:]

    if len(values) != len(data_columns):
        raise ValueError(
            "Количество значений не соответствует количеству столбцов."
        )

    for value, column in zip(values, data_columns):
        column_name, column_type = column

        if column_type == "int" and type(value) is not int:
            raise ValueError(
                f"Поле {column_name} должно иметь тип int."
            )

        if column_type == "str" and type(value) is not str:
            raise ValueError(
                f"Поле {column_name} должно иметь тип str."
            )

        if column_type == "bool" and type(value) is not bool:
            raise ValueError(
                f"Поле {column_name} должно иметь тип bool."
            )

    table_data = load_table_data(table_name)

    new_id = max(
        (record["ID"] for record in table_data),
        default=0,
    ) + 1

    record = {"ID": new_id}

    for column, value in zip(data_columns, values):
        column_name = column[0]
        record[column_name] = value

    table_data.append(record)

    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )

    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Select records from table data."""
    if where_clause is None:
        return table_data

    return [
        record
        for record in table_data
        if all(
            record.get(column) == value
            for column, value in where_clause.items()
        )
    ]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Update records matching the condition."""
    updated_ids = []

    for record in table_data:
        matches = all(
            record.get(column) == value
            for column, value in where_clause.items()
        )

        if matches:
            record.update(set_clause)
            updated_ids.append(record["ID"])

    return table_data, updated_ids


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Delete records matching the condition."""
    deleted_ids = [
        record["ID"]
        for record in table_data
        if all(
            record.get(column) == value
            for column, value in where_clause.items()
        )
    ]

    remaining_data = [
        record
        for record in table_data
        if record["ID"] not in deleted_ids
    ]

    return remaining_data, deleted_ids