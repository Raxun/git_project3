import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Roles(SqlAlchemyBase):
    __tablename__ = 'roles'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_server = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    id_owner = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    banned_role = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    admitted_users = sqlalchemy.Column(sqlalchemy.String, nullable=True)

