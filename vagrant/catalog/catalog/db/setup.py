from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


from catalog.config import SQL_COMMAND
Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column( Integer, ForeignKey('category_id.id'))
    category = relationship(Category)


engine_factory = create_engine(SQL_COMMAND)
Base.metadata.create_all(engine_factory)
