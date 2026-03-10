# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()]) # !!!!!!!
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembre-se de mim')
    submit = SubmitField('Entrar')
    
class RegistrationForm(FlaskForm):
    username = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField('Confirmação de senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Por favor use um email diferente.')

class EditProfileForm(FlaskForm):
    username = StringField('Nome', validators=[DataRequired()])
    about_me = TextAreaField('Sobre mim', validators=[Length(min=0, max=140)])
    submit = SubmitField('Salvar')
    
class TarefaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    tipo = StringField('Tipo', validators=[Optional(), Length(max=128)])
    data_programada = DateTimeField('Data Programada', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class TrocaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    local = StringField('Local', validators=[DataRequired(), Length(max=128)])
    descricao = TextAreaField('Descrição', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Salvar')