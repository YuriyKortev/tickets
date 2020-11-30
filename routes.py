from flask import render_template, redirect, url_for, request, flash, current_app, session, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_principal import RoleNeed, ActionNeed, Permission,\
    identity_loaded, Identity, identity_changed, AnonymousIdentity
from werkzeug.urls import url_parse
from app import app
from utils.models import Person, City, path_filter, DoesNotExist, Air_flight, Air_class, Train_class, Train_ride,\
    SeatType, week_end, week_start
from utils.forms import SearchForm_air, LoginForm, RegistrationForm, SearchForm_train, SearchRide
from utils.stats import get_week_stats, get_pie, get_range_stats
from datetime import datetime


@app.route('/')
@app.route('/air')
def start_page():
    return render_template('main.html', form=SearchForm_air())


@app.route('/train')
def start_page_train():
    return render_template('main.html', form=SearchForm_train())


admin = Permission(RoleNeed('admin'))


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'is_admin'):
        if identity.user.is_admin:
            identity.provides.add(RoleNeed('admin'))


@app.route('/admin/get_pie')
@login_required
@admin.require(http_exception=403)
def render_pie():
    form = SearchRide(request.args)
    if form.validate():
        if form.ride_type.data == 'Air_flight':
            ride_type = Air_flight
        elif form.ride_type.data == 'Train_ride':
            ride_type = Train_ride
        else:
            ride_type = Air_flight
        bought_seats, free_seats = ride_type.get_ride_stats(form.city_from.data, form.city_to.data, form.date_to.data)
        pie_image = get_pie(bought_seats, free_seats)

        return pie_image

    return jsonify(data=form.errors)


@app.route('/admin/get_range_stats')
@login_required
@admin.require(http_exception=403)
def render_range_stats():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    air_stats = Air_class.get_num_of_sold_tickets_in_date_range(start_date, end_date)
    train_stats = Train_class.get_num_of_sold_tickets_in_date_range(start_date, end_date)

    image = get_range_stats(air_stats, train_stats)

    return image


@app.route('/admin')
@login_required
@admin.require(http_exception=403)
def admin():
    bought_air_today = Air_class.get_num_of_sold_tickets_today()
    bought_train_today = Train_class.get_num_of_sold_tickets_today()
    stats_on_week_air = Air_class.get_num_of_sold_tickets_on_current_week()
    stats_on_week_train = Train_class.get_num_of_sold_tickets_on_current_week()
    stats_in_date_range_air = stats_on_week_air
    stats_in_date_range_train = stats_on_week_train
    most_popular_air_ticket = Air_class.get_most_popular_ticket()
    most_popular_train_ticket = Train_class.get_most_popular_ticket()

    return render_template('admin.html',
                           bought_air_today=bought_air_today,
                           bought_train_today=bought_train_today,
                           image_week_stats=get_week_stats(stats_on_week_air, stats_on_week_train),
                           image_range_stats=get_range_stats(stats_in_date_range_air, stats_in_date_range_train),
                           most_popular_air_ticket=most_popular_air_ticket,
                           most_popular_train_ticket=most_popular_train_ticket,
                           week_start=week_start,
                           week_end=week_end,
                           form=SearchRide())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('start_page'))
    form = LoginForm()
    if form.validate_on_submit():
        print('name: {}, password: {}, remember me: {}'.format(form.username.data, form.password.data, form.remember_me.data))
        user = Person.nodes.get_or_none(name=form.username.data)

        if user is None or not user.check_password(form.password.data):
            flash('Неправильный логин или пароль!!!')
            return redirect(url_for('login'))

        login_user(user, form.remember_me.data)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('start_page')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/train/buy_ticket', methods=['GET', 'POST'])
@login_required
def buy_train_ticket():
    args = request.args.getlist('id')
    if request.method == 'GET':
        print(args)
        tickets = Train_class.get_tickets(args, current_user)
        return render_template('buy_tickets.html', tickets=tickets,
                               bought=all([ticket['already_bought'] for ticket in tickets]))

    elif request.method == 'POST':
        res = [current_user.register_on_train_ticket(class_id) for class_id in args]
        print(all(res))
        if all(res):
            return 'True'
        else:
            return 'False'


@app.route('/air/buy_ticket', methods=['GET', 'POST'])
@login_required
def buy_air_ticket():
    args = request.args.getlist('id')
    if request.method == 'GET':
        print(args)
        tickets = Air_class.get_tickets(args, current_user)
        return render_template('buy_tickets.html', tickets=tickets,
                               bought=all([ticket['already_bought'] for ticket in tickets]))

    elif request.method == 'POST':
        res = [current_user.register_on_air_ticket(class_id) for class_id in args]
        print(all(res))
        if all(res):
            return 'True'
        else:
            return 'False'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Person(name=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password_hash(form.password.data)
        user.is_admin = False
        user.save()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()

    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('start_page'))


def search(form, ride_type):
    form = form(request.args)
    error_messages = []
    if form.validate():
        try:
            city_from = City.nodes.get(name=form.city_from.data)
            city_to = City.nodes.get(name=form.city_to.data)
        except DoesNotExist:
            error_messages.append('Такого города не существует!')
            return render_template('search_errors.html', form=form, errors=error_messages)

        paths_to = city_from.ways_to(form.city_to.data, int(form.class_.data), ride_type)
        paths_to = list(filter(path_filter(form.date_to.data), paths_to))

        paths_back = city_to.ways_to(form.city_from.data, int(form.class_.data), ride_type)
        paths_back = list(filter(path_filter(form.date_back.data), paths_back))

        return render_template('search_results.html',
                               paths_to=paths_to,
                               paths_back=paths_back,
                               form=form)


@app.route('/air/search/', methods=['GET'])
def search_air():
    return search(SearchForm_air, Air_flight)


@app.route('/train/search/', methods=['GET'])
def search_train():
    return search(SearchForm_train, Train_ride)


if __name__ == '__main__':
    app.run()