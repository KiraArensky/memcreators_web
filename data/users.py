import datetime
import os
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash
from PIL import Image

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    login = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    about = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    picture = sqlalchemy.Column(sqlalchemy.String,
                                index=True, unique=True, nullable=True)

    news = orm.relationship("News", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def avatar(self, us, db, filename):
        im = Image.open(f'static/user_pic/{filename}')
        img_width, img_height = im.size
        img = im.crop(((img_width - 200) // 2,
                       (img_height - 200) // 2,
                       (img_width + 200) // 2,
                       (img_height + 200) // 2))
        us.picture = f'static/user_pic/{filename}'
        os.remove(f'static/user_pic/{filename}')
        img.save(f'static/user_pic/{filename}', quality=95)
        us.created_date = datetime.datetime.now()
        db.commit()
