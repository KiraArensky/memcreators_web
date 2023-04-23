from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm, SerializerMixin):
    name = StringField('Название', validators=[DataRequired()])
    about = StringField("Описание")
    submit = SubmitField('Опубликовать')
    private = BooleanField('Приватный пост')