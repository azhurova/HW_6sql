import json
from prettytable import PrettyTable

import sqlalchemy
from sqlalchemy.orm import sessionmaker

import models
from models import Publisher, Book, Shop, Stock, Sale

# подключение к БД PostgreSQL;
DSN = "postgresql://postgres:331350@localhost:5432/postgres"
engine = sqlalchemy.create_engine(DSN)

# создание необходимых моделей данных;
models.create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

# заполнение БД тестовыми данными
with open('tests_data.json', 'r') as fd:
    data = json.load(fd)

for record in data:
    model = globals()[record.get('model').title()]
    session.add(model(id=record.get('pk'), **record.get('fields')))
    for row in session.query(model).all():
        print(row)
session.commit()
print()

# принимает имя или идентификатор издателя (publisher), например, через input(). Выводит построчно факты покупки книг этого издателя:
publisher_name = 'Pearson'  # input("Введите имя издателя (publisher): ")
q = session.query(Publisher).filter(Publisher.name == publisher_name)

if q.count() == 0:
    print(f'Издатель с именем "{publisher_name}" не найден!')
print()

q = session.query(Book, Shop, Sale)
q = q.join(Stock, Stock.id == Sale.id_stock)
q = q.join(Book, Book.id == Stock.id_book)
q = q.join(Shop, Shop.id == Stock.id_shop)
q = q.join(Publisher, Publisher.id == Book.id_publisher)

# название книги | название магазина, в котором была куплена эта книга | стоимость покупки | дата покупки
table = PrettyTable()
table.field_names = ["Book name", "Shop name", "Sale price", "Sale date"]
for book, shop, sale in q.all():
    table.add_rows([[book.title, shop.name, sale.price, sale.date_sale]])

print(table)
session.close()
