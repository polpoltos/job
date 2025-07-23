import pandas as pd

# Загрузите ваш Excel файл
xlsx = pd.ExcelFile('отгрузка на заводы, комплекты.xlsx')

# Загрузите листы в DataFrame
df1 = pd.read_excel(xlsx, 'Конечные пользователи (Не трога')
df2 = pd.read_excel(xlsx, 'Конечники (продажи)')
df1['ИНН Клиента'] = df1['ИНН Клиента'].astype(str)
df2['ИНН Клиента'] = df2['ИНН Клиента'].astype(str)

# Сравните столбец 'A' в каждом листе
comparison = df1['ИНН Клиента'].isin(df2['ИНН Клиента'])

# Создайте новый DataFrame для записи результатов
df3 = pd.DataFrame()
df3['ИНН Клиента'] = df1['ИНН Клиента'].astype(str)
df3['Comparison'] = comparison
df3['Source Sheet'] = df3['ИНН Клиента'].apply(lambda x: 'Конечные пользователи (Не трога' if x in df1['ИНН Клиента'].values else ('Конечники (продажи)' if x in df2['ИНН Клиента'].values else 'None'))

# Удалите дубликаты
df3.drop_duplicates(subset='ИНН Клиента', keep='first', inplace=True)

with pd.ExcelWriter('отгрузка на заводы, комплекты.xlsx', mode='a') as writer:
    df3.to_excel(writer, sheet_name='Сравнение1')


comparison = df2['ИНН Клиента'].isin(df1['ИНН Клиента'])

# Создайте новый DataFrame для записи результатов
df3 = pd.DataFrame()
df3['ИНН Клиента'] = df2['ИНН Клиента'].astype(str)
df3['Comparison'] = comparison
df3['Source Sheet'] = df3['ИНН Клиента'].apply(lambda x: 'Конечные пользователи (Не трога' if x in df1['ИНН Клиента'].values else ('Конечники (продажи)' if x in df2['ИНН Клиента'].values else 'None'))

# Удалите дубликаты
df3.drop_duplicates(subset='ИНН Клиента', keep='first', inplace=True)

with pd.ExcelWriter('отгрузка на заводы, комплекты.xlsx', mode='a') as writer:
    df3.to_excel(writer, sheet_name='Сравнение2')
