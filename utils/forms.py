from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional, ValidationError, Email, EqualTo
from utils.models import Person


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
            raise ValidationError('{} always exists!!'.format(username.data))


class SearchRide(FlaskForm):
    ride_type = SelectField('Поездка', choices=[('Air_flight', 'Полёт'), ('Train_ride', 'Поездка')],
                            validators=[DataRequired()])
    city_from = StringField('Откуда', validators=[DataRequired()])
    city_to = StringField('Куда', validators=[DataRequired()])
    date_to = DateField('Туда', validators=[DataRequired()])
    submit = SubmitField('Поиск')


