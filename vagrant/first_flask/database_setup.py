import sys

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import table, column

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from config import SQL_COMMAND



class Base(object):
    # https://stackoverflow.com/questions/13978554/is-possible-to-create-column-in-sqlalchemy-which-is-going-to-be-automatically-po
    def __tablename__(self):
        return self.__name__.lower()
    id = Column(Integer, primary_key=True)
    last_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


Base = declarative_base(cls = Base)


class Restaurant(Base):
    __tablename__ = 'restaurant'
    name = Column(String(80), nullable=False)


class MenuItem(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80),nullable=False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column( Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)


engine = create_engine(SQL_COMMAND)

Base.metadata.create_all(engine)