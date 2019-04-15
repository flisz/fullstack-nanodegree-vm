import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog.config import SQL_COMMAND
Base = declarative_base()

class Category(Base):
    __tablename__ = 'restaurant'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class Item(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80),nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column( Integer, ForeignKey('category_id.id'))
    category = relationship(Category)


engine_factory = create_engine(SQL_COMMAND)
Base.metadata.create_all(engine_factory)
Base.metadata.bind = engine_factory
DBSessionMaker = sessionmaker(bind=engine)


def get_session():
    return DBSessionMaker()


def add_category(data):
    required = dict()
    required["name"] = data.get("name")

    print("trying to add new category:\n\tinput_data:\t{}".format(data))
    if name is None:
        print('insufficient required data provided!\n\trequired_data:\t{}'.format(required))
    else:
        category = Category()
        category.name = data['name']
        session = get_session()
        session.add(category)
        session.commit()
        print('success!')


def update_category(data):
    required = dict()
    required["category_id"] = data.get("category_id")
    required["name"] = data.get("name")
    print("trying to update category:\n\tinput_data:\t{}".format(data))
    if any([requirement is None for requirement in required.items()]):
        print('insufficient required data provided!\n\trequired_data:\t{}'.format(required))
    else:
        session = get_session()
        categories = session.query(Category).filter(Category.id == required["category_id"])
        for category in categories:
            category.name = required["name"]
        session.commit()







    return create_engine(SQL_COMMAND)
engine = create_engine(SQL_COMMAND)
Base.metadata.create_all(engine)
