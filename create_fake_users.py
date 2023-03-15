import random
import sys
from faker import Faker
from bootstrap_table import db, User


def create_fake_users(n):
    """Создаёт рандомных пользователей для базы данных"""
    faker = Faker()
    for i in range(n):
        user = User(name=faker.name(),
                    age=random.randint(20, 80),
                    address=faker.address().replace('\n', ', '),
                    phone=faker.phone_number(),
                    email=faker.email())
        db.session.add(user)
    db.session.commit()
    print(f'Сгенерировано {n} рандомных пользователей для базы данных.')


if __name__ == '__main__':
    # if len(sys.argv) <= 1:
    #     print('Pass the number of users you want to create as an argument.')
    #     sys.exit(1)
    create_fake_users(int(input('Введите количество записей, которое необходимо сгенерировать: ')))
