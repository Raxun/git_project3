import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_server = sqlalchemy.Column(sqlalchemy.Integer)
    id_user = sqlalchemy.Column(sqlalchemy.Integer)
    NumberOfMessage = sqlalchemy.Column(sqlalchemy.String)
    lvl = sqlalchemy.Column(sqlalchemy.Integer)

