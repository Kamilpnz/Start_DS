import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from urllib.parse import urlparse, urlunparse, quote
from io import StringIO
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings


st.header('Динамика заработной платы по отраслям')

df_1 = pd.read_excel('tab3-zpl_2023.xlsx', 
                     sheet_name=0, 
                     skiprows=5, 
                     names=['name', '2017', '2018', '2019', '2020', '2021', '2022', '2023'],
                     skipfooter=3,
                    index_col=0)


df_1 = df_1 \
    .dropna() \
    .rename(index={'деятельность гостиниц и предприятий общественного питания': 'гостиницы и рестораны'})

df_1.index = df_1.index.str.strip()


df_1_main = df_1.loc[['гостиницы и рестораны', 'добыча полезных ископаемых', 'образование']]


df_2 = pd.read_excel('tab3-zpl_2023.xlsx', 
                     sheet_name=1, 
                     skiprows=2, 
                     header=0,
                     skipfooter=2,
                    index_col=0)

df_2 = df_2.rename(columns={'Unnamed: 0': 'name'},
                  index={'Добыча полезных ископаемых': 'добыча полезных ископаемых',
                         'Гостиницы и рестораны': 'гостиницы и рестораны',
                         'Образование': 'образование'}) \
            .dropna()


df_2_main = df_2.loc[['добыча полезных ископаемых', 'гостиницы и рестораны', 'образование']]

df_main = df_2_main.merge(df_1_main, left_index=True, right_index=True)

st.dataframe(df_main)

# st.table(df_main)

df_main = df_main.T

df_main.index = df_main.index.astype(int)


# Создание графика
plt.figure(figsize=(10, 6))
# sns.lineplot(x='date', y='value', data=df_main)
sns.lineplot(data=df_main)
plt.title('Динамика номинальной заработной платы')
plt.xlabel('Год')
plt.ylabel('Заработная плата, руб')


st.pyplot(plt)

def encode_punycode(url):
    # Разбиваем URL на компоненты
    parsed_url = urlparse(url)
    # Кодируем доменное имя в Punycode
    encoded_domain = parsed_url.hostname.encode('idna').decode('ascii')
    # Кодируем путь для безопасной передачи через URL
    encoded_path = quote(parsed_url.path)
    # Возвращаем перекодированный URL
    return urlunparse(parsed_url._replace(netloc=encoded_domain, path=encoded_path))

# Отключаем предупреждения SSL
disable_warnings(InsecureRequestWarning)

# Исходный URL
url = 'https://уровень-инфляции.рф/таблицы-инфляции'

# Кодирование доменного имени и пути в Punycode/URL-код
encoded_url = encode_punycode(url)
print("Encoded URL:", encoded_url)

# Пытаемся загрузить данные, игнорируя проверку SSL
try:
    response = requests.get(encoded_url, verify=False)
    # Использование StringIO для считывания HTML
    html_data = StringIO(response.text)
    tables = pd.read_html(html_data)  # Используем StringIO объект для pandas
    # print(f"Найдено таблиц: {len(tables)}")
    if tables:
        df_inf = tables[0]
    #     # Опционально: сохранение таблиц в CSV
    #     for i, table in enumerate(tables):
    #         table.to_csv(f'table_{i+1}.csv', index=False)
    #     print("Таблицы сохранены в файлы CSV.")
    # else:
    #     print("На странице не найдены таблицы.")
except Exception as e:
    print("Произошла ошибка при загрузке таблиц:", e)


df_inf = df_inf.set_index('Год') \
    .rename(columns={'Всего': 'inf_rate'})

df_inf = df_inf['inf_rate']

df_inf = df_inf.sort_index(ascending=True)
df_inf = df_inf.T

st.header('Данные по инфляции по годам')

# st.dataframe(df_inf)

st.table(df_inf)


df_main = df_main.merge(df_inf, how='left', left_index=True, right_index=True)

df_main = df_main.assign(real_добыча_полезных_ископаемых = df_main[['добыча полезных ископаемых']].apply(lambda x: x / (1 + df_main['inf_rate'] / 100)).round(2), 
        real_гостиницы_и_рестораны = df_main[['гостиницы и рестораны']].apply(lambda x: x / (1 + df_main['inf_rate'] / 100)).round(2), 
        real_образование = df_main[['образование']].apply(lambda x: x / (1 + df_main['inf_rate'] / 100)).round(2))


st.header('Данные номинальной и реальной заработной платы по отраслям')
st.table(df_main)


# Создание фигуры с графиками
plt.figure(figsize=(14, 4))

plt.subplot(131)
sns.lineplot(data=df_main[['добыча полезных ископаемых', 'real_добыча_полезных_ископаемых']])
plt.title('Добыча полезных ископаемых')

plt.subplot(132)
sns.lineplot(data=df_main[['гостиницы и рестораны', 'real_гостиницы_и_рестораны']])
plt.title('Гостиницы и рестораны')

plt.subplot(133)
sns.lineplot(data=df_main[['образование', 'real_образование']])
plt.title('Образование')

plt.suptitle('Динамика номинальной и реальной заработной платы по отраслям')

# Отображение графика в Streamlit
st.pyplot(plt)






