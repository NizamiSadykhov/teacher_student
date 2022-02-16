from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length

from config import conn


class RegistrationForm(FlaskForm):
    Name = StringField('Name', validators=[DataRequired()])
    Username = StringField('Username', validators=[DataRequired()])
    Email = StringField('Email', validators=[DataRequired(), Email()])
    Group = StringField('Group', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        cursor = conn.cursor()
        cursor.execute("SELECT login FROM student ")
        loginList = cursor.fetchall()
        for login in loginList:
            if username.data == login[0]:
                raise ValidationError('Этот username уже занят, попробуйте другой')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    who_are_you = StringField('who_are_you', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_who_are_you(self, who_are_you):
        if who_are_you == 'Who are you?':
            raise ValidationError('You must choose')

class ChangeMarkForm(FlaskForm):
    mark = StringField('Mark', validators=[DataRequired()])
    date = StringField('date', validators=[DataRequired()])
    LR_name = StringField('LR_name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileFormStudent(FlaskForm):
    name = StringField('Имя', validators=[Length(min=0, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

class EditProfileFormTeacher(FlaskForm):
    name = StringField('Имя', validators=[Length(min=0, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

class AddLrForm(FlaskForm):
    name = StringField('Имя', validators=[Length(min=0, max=25)])
    submit = SubmitField('Submit')