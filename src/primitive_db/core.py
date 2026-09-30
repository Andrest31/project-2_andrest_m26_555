"""Core database operations."""

from src.primitive_db.constants import VALID_TYPES


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


def drop_table(metadata, table_name):
    """Delete a table from database metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata