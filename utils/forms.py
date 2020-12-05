from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, \
    IntegerField
from wtforms.validators import DataRequired, Optional, ValidationError, Email, EqualTo
from utils.models import Person, Airport, Station, City
from wtforms.fields.html5 import DateTimeLocalField
from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SearchForm(FlaskForm):
    city_from = StringField('Откуда', validators=[DataRequired()])
    city_to = StringField('Куда', validators=[DataRequired()])
    date_to = DateField('Туда', validators=[Optional()])
    date_back = DateField('Обратно', validators=[Optional()])
    submit = SubmitField('Поиск')


class SearchForm_air(SearchForm):
    class_ = SelectField(u'Класс', choices=[(1, 'Эконом'), (2, 'Бизнес'), (3, 'Первый')])
    action = 'search_air'


class SearchForm_train(SearchForm):
    class_ = SelectField(u'Класс', choices=[(1, 'Плацкарт'), (2, 'Купе'), (3, 'СВ')])
    action = 'search_train'


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = Person.nodes.get_or_none(email=email.data)
        if user is not None:
            raise ValidationError('Please use a different email.')

    def validate_username(form, username):
        user = Person.nodes.get_or_none(name=username.data)
        if user is not None:
            raise ValidationError('{} already exists!!'.format(username.data))


class SearchRide(FlaskForm):
    ride_type = SelectField('Поездка', choices=[('Air_flight', 'Полёт'), ('Train_ride', 'Поездка')],
                            validators=[DataRequired()])
    city_from = StringField('Откуда', validators=[DataRequired()])
    city_to = StringField('Куда', validators=[DataRequired()])
    date_from = DateField('Отправление', validators=[DataRequired()])
    submit = SubmitField('Поиск')


class CreateRide(FlaskForm):
    ride_type = SelectField('Поездка', choices=[('Air_flight', 'Полёт'), ('Train_ride', 'Поездка')],
                            validators=[DataRequired()])
    station_from = StringField('Откуда (Аэропорт или станция)', validators=[DataRequired()])
    station_to = StringField('Куда (Аэропорт или станция)', validators=[DataRequired()])
    date_to = DateTimeLocalField('Прибытие', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    date_from = DateTimeLocalField('Отправление', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Создать')

    def validate_station_from(form, station):
        if form.ride_type.data == 'Air_flight':
            st = Airport.nodes.get_or_none(name=station.data)
        else:
            st = Station.nodes.get_or_none(name=station.data)
        if st is None:
            raise ValidationError('Такой станции нет!!!!')

    def validate_station_to(form, station):
        if form.ride_type.data == 'Air_flight':
            st = Airport.nodes.get_or_none(name=station.data)
        else:
            st = Station.nodes.get_or_none(name=station.data)
        if st is None:
            raise ValidationError('Такой станции нет!!!!')

    def validate_date_to(form, date):
        if form.date_from.data is None:
            raise ValidationError('Введите дату!!!!!!!!!')
        if date.data < form.date_from.data:
            raise ValidationError('Дата прибытия должна быть позже!!!!!!')


class CreateCity(FlaskForm):
    city_name = StringField('Название Города', validators=[DataRequired()])
    submit = SubmitField('Создать')

    def validate_city_name(form, city_n):
        city = City.nodes.get_or_none(name=city_n.data)
        if city:
            raise ValidationError('Такой город уже сущетсвует!!!!!!!!!!!!!')


class CreateStation(FlaskForm):
    station_type = SelectField('Тип станции', choices=[('Airport', 'Аэропорт'), ('Station', 'ЖД станция')],
                               validators=[DataRequired()])
    station_name = StringField('Название станции', validators=[DataRequired()])
    station_location = SelectField('Местоположение', coerce=str)

    submit = SubmitField('Создать')


