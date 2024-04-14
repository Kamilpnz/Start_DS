import requests
import pandas as pd
from urllib.parse import urlparse, urlunparse, quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings

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
    tables = pd.read_html(response.text)  # Используем text ответа для pandas
    print(f"Найдено таблиц: {len(tables)}")
    if tables:
        # Опционально: сохранение таблиц в CSV
        for i, table in enumerate(tables):
            table.to_csv(f'table_{i+1}.csv', index=False)
        print("Таблицы сохранены в файлы CSV.")
    else:
        print("На странице не найдены таблицы.")
except Exception as e:
    print("Произошла ошибка при загрузке таблиц:", e)
