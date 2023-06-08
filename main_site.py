from flask import Flask, render_template, request, abort, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class Incidents(db.Model):
    """Класс инцидентов (заявок клиентов)"""
    incident = db.Column(db.Integer, primary_key=True)  # Инцидент
    created = db.Column(db.String(32), index=True)  # Создана
    completed = db.Column(db.String(32), index=True)  # Выполнено
    status = db.Column(db.String(64), index=True)  # Статус
    SN = db.Column(db.String(64), index=True)  # Серийный номер
    model = db.Column(db.String(64), index=True)  # Модель
    service = db.Column(db.String(64), index=True)  # Сервис
    contacting = db.Column(db.String(128), index=True)  # Обращение
    result = db.Column(db.String(128), index=True)  # Результат
    address = db.Column(db.String(64), index=True)  # Адрес
    office = db.Column(db.String(32), index=True)  # Кабинет
    department = db.Column(db.String(64), index=True)  # Отдел
    contact_person = db.Column(db.String(64), index=True)  # Контактное лицо
    phone = db.Column(db.String(32), index=True)  # Телефон
    contractor = db.Column(db.String(32), index=True)  # Исполнитель
    order = db.Column(db.String(32), index=True)  # Наряд

    def to_dict(self):
        return {
            'incident': self.incident,
            'created': self.created,
            'status': self.status,
            'model': self.model,
            'service': self.service,
            'phone': self.phone
        }


class User(UserMixin, db.Model):
    """Класс пользователей"""
    id = db.Column(db.Integer, primary_key=True)  # Идентификационный номер
    login = db.Column(db.String(64))  # Логин
    password = db.Column(db.String(150))  # Пароль
    access_level = db.Column(db.Integer)  # Уровень доступа

    def to_dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'password': self.password,
            'access_level': self.access_level
        }


db.create_all()


# Отрисовка самой таблицы, деструктор login_required запрещает зайти на страничку не авторизованным пользователям
@app.route('/table')
@login_required
def index():
    """Отрисовка странички с таблицей инцидентов"""
    return render_template('incidents_table.html', login=current_user.login)


@app.route('/users_table')
@login_required
def users():
    """Отрисовка странички с таблицей пользователей"""
    return render_template('users_table.html')


@login_manager.user_loader
def load_user(user_id):
    """Поскольку user_id является первичным ключом нашей таблицы пользователей,
    используйте его в запросе для пользователя"""
    return User.query.get(int(user_id))


@app.route('/update_incident')
@login_required
def users_update():
    """Отрисовка странички с таблицей функционала"""
    return render_template('update_incident.html')


@app.route('/login')
def login():
    """Отрисовка странички авторизации"""
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    """Создание функционала на страничке авторизации"""
    login = request.form.get('login')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(login=login).first()

    # проверить, существует ли пользователь на самом деле
    # взять пароль, предоставленный пользователем, хэшировать его и сравнить с хэшированным паролем в базе данных
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))
        # если пользователь не существует или пароль неверен, перезагрузить страницу
    # если вышеуказанная проверка пройдена, то мы знаем, что пользователь имеет правильные учетные данные
    login_user(user, remember=remember)
    return redirect(url_for('index'))


@app.route('/del_user')
@login_required
def del_user():
    """Отрисовка странички удаления пользователя"""
    return render_template('del_user.html')


@app.route('/del_user', methods=['POST'])
@login_required
def del_user_post():
    """Создание функционала на страничке удаления пользователя"""
    # Код для проверки и удаления пользователя из БД находится здесь
    id = request.form.get('id')

    # Если возвращается пользователь, то этот логин уже существует в базе данных
    user = User.query.filter_by(id=id).first()

    # Если пользователь не найден, то страничка обновляется
    if not user:
        flash('Такого пользователя не существует')
        return redirect(url_for('del_user'))

    # удаляет пользователя из БД
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/signup')
@login_required
def signup():
    """Отрисовка странички регистрации"""
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
@login_required
def signup_post():
    """Создание функционала на страничке регистрации"""
    # Код для проверки и добавления пользователя в базу данных находится здесь
    login = request.form.get('login')
    password = request.form.get('password')
    access_level = request.form.get('access_level')

    # Если возвращается пользователь, то этот логин уже существует в базе данных
    user = User.query.filter_by(login=login).first()

    # Если пользователь найден, то страничка обновляется
    if user:
        flash('Такой пользователь уже существует')
        return redirect(url_for('signup'))

    # Создание нового пользователя с данными формы. Хеширование пароля, чтобы не сохранялась версия с открытым текстом
    new_user = User(login=login, password=generate_password_hash(password, method='sha256'), access_level=access_level)

    # добавить нового пользователя в базу данных
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('users'))


@app.route('/api/data')
@login_required
def data():
    """Страничка, где хранятся данные"""
    query = Incidents.query

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Incidents.incident.like(f'%{search}%'),
            Incidents.created.like(f'%{search}%'),
            Incidents.status.like(f'%{search}%'),
            Incidents.model.like(f'%{search}%'),
            Incidents.service.like(f'%{search}%'),
            Incidents.phone.like(f'%{search}%')
        ))
    total = query.count()

    # sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            service = s[1:]
            if service not in ['incident', 'created', 'status', 'model', 'service', 'phone']:
                service = 'service'
            col = getattr(Incidents, service)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    # response
    return {
        'data': [incidents.to_dict() for incidents in query],
        'total': total,
    }


@app.route('/api/data', methods=['POST'])
@login_required
def update():
    """Создание функционала на страничке, где хранятся данные"""
    data = request.get_json()
    if 'incident' not in data:
        abort(400)
    incidents = Incidents.query.get(data['incident'])
    for field in ['created', 'status', 'model', 'service', 'phone']:
        if field in data:
            setattr(incidents, field, data[field])
    db.session.commit()
    return '', 204


###############
@app.route('/api1/data_api1')
def data_api1():
    query = User.query

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            User.id.like(f'%{search}%'),
            User.login.like(f'%{search}%'),
            User.password.like(f'%{search}%'),
            User.access_level.like(f'%{search}%')
        ))
    total = query.count()

    # sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            login = s[1:]
            if login not in ['id', 'login', 'access_level']:
                login = 'name'
            col = getattr(User, login)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'total': total,
    }


@app.route('/api1/data_api1', methods=['POST'])
def update_api1():
    data = request.get_json()
    if 'id' not in data:
        abort(400)
    user = User.query.get(data['id'])
    for field in ['id', 'login', 'password', 'access_level']:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
