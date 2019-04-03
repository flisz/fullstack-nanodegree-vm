from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query

from config import SQL_COMMAND
from database_setup import Restaurant, Base, MenuItem

engine = create_engine(SQL_COMMAND)
#Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DB = sessionmaker(bind=engine)
session = DB()
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, "you can
# revert all of them back to the last commit by calling
# session.rollback()    
