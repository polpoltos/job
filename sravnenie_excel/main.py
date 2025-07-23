import pandas as pd


def merge_columns(file1, file2, key_column, value_column, output_file=None):
    """
    Сопоставляет строки по ключевому столбцу и объединяет значения второго столбца из обоих файлов.

    :param file1: Путь к первому файлу Excel (.xlsx)
    :param file2: Путь ко второму файлу Excel (.xlsx)
    :param key_column: Название столбца для сопоставления (например, 'Рег.номер')
    :param value_column: Название второго столбца, который нужно вывести
    :param output_file: (Необязательно) Путь для сохранения результата в Excel
    """
    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return

    # Проверяем, что указанные столбцы существуют
    for col in [key_column, value_column]:
        if col not in df1.columns or col not in df2.columns:
            print(f"Ошибка: столбец '{col}' отсутствует в одном из файлов.")
            return

    # Преобразуем названия столбцов в верхний регистр
    df1.columns = df1.columns.str.upper()
    df2.columns = df2.columns.str.upper()
    key_column = key_column.upper()
    value_column = value_column.upper()

    # Переименовываем столбцы для удобства
    df1 = df1[[key_column, value_column]].rename(columns={value_column: 'ЗНАЧЕНИЕ_ФАЙЛ1'})
    df2 = df2[[key_column, value_column]].rename(columns={value_column: 'ЗНАЧЕНИЕ_ФАЙЛ2'})
    print(df1)

    # Объединяем данные по ключевому столбцу
    merged_df = pd.merge(df1, df2.upper, on=key_column, how='outer')

    # Выводим результат
    print(merged_df)

    # Сохраняем в файл, если указан путь
    if output_file:
        merged_df.to_excel(output_file, index=False)
        print(f"Результат сохранен в {output_file}")


# Пример использования:
merge_columns("1.xlsx", "2.xlsx", "Рег.номер", "Подразделение", "output.xlsx")
