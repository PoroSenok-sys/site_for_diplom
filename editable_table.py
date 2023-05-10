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


class a():
    pass


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True)
    age = db.Column(db.Integer, index=True)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    password = db.Column(db.String(150))

    def to_dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'age': self.age,
            'address': self.address,
            'phone': self.phone,
            'email': self.email
        }


db.create_all()


# Отрисовка самой таблицы, деструктор login_required запрещает зайти на страничку не авторизованным пользователям
@app.route('/table')
@login_required
def index():
    return render_template('editable_table.html', login=current_user.login)


@login_manager.user_loader
def load_user(user_id):
    # поскольку user_id является первичным ключом нашей таблицы пользователей,
    # используйте его в запросе для пользователя
    return User.query.get(int(user_id))


# Отрисовка странички авторизации
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
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
    return render_template('del_user.html')


@app.route('/del_user', methods=['POST'])
@login_required
def del_user_post():
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
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
@login_required
def signup_post():
    # Код для проверки и добавления пользователя в базу данных находится здесь
    login = request.form.get('login')
    password = request.form.get('password')

    # Если возвращается пользователь, то этот логин уже существует в базе данных
    user = User.query.filter_by(login=login).first()

    # Если пользователь найден, то страничка обновляется
    if user:
        flash('Такой пользователь уже существует')
        return redirect(url_for('signup'))

    # Создание нового пользователя с данными формы. Хеширование пароля, чтобы не сохранялась версия с открытым текстом
    new_user = User(login=login, password=generate_password_hash(password, method='sha256'), age=None, address=None,
                    phone=None, email=None)

    # добавить нового пользователя в базу данных
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/api/data')
@login_required
def data():
    query = User.query

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            User.id.like(f'%{search}%'),
            User.login.like(f'%{search}%'),
            User.email.like(f'%{search}%')
        ))
    total = query.count()

    # sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            login = s[1:]
            if login not in ['id', 'login', 'age', 'email']:
                login = 'login'
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


@app.route('/api/data', methods=['POST'])
@login_required
def update():
    data = request.get_json()
    if 'id' not in data:
        abort(400)
    user = User.query.get(data['id'])
    for field in ['login', 'age', 'address', 'phone', 'email']:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    app.run()
