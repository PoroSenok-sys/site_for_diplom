import random
import sys
from faker import Faker
from editable_table import db, User
from werkzeug.security import generate_password_hash, check_password_hash


def create_fake_users(n):
    """Создаёт рандомных пользователей для базы данных"""
    faker = Faker("ru_RU")
    for i in range(n):
        login_1 = faker.first_name()
        user = User(login=login_1,
                    age=random.randint(20, 80),
                    address=faker.address().replace('\n', ', '),
                    phone=faker.phone_number(),
                    email=faker.email(),
                    password=generate_password_hash(login_1, method='sha256'))
        db.session.add(user)
    db.session.commit()
    print(f'Сгенерировано {n} рандомных пользователей для базы данных.')


if __name__ == '__main__':
    # if len(sys.argv) <= 1:
    #     print('Pass the number of users you want to create as an argument.')
    #     sys.exit(1)
    create_fake_users(int(input('Введите количество записей, которое необходимо сгенерировать: ')))
