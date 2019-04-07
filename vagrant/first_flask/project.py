from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query

from config import SQL_COMMAND
from database_setup import Restaurant, Base, MenuItem

engine = create_engine(SQL_COMMAND)
Base.metadata.bind = engine
DBSessionMaker = sessionmaker(bind=engine)
session = DBSessionMaker()

@app.route('/', methods=['GET'])
@app.route('/restaurants', methods=['GET'])
def restaurants():
    restaurants = session.query(Restaurant)
    restaurants_headers = restaurants.column_descriptions
    output = ''
    # Main Table:
    table_object = Restaurant
    subtable_objects = MenuItem
    output += html_table_with_subtables(output, 
								    	table_object=table_object, 
								    	subtable_objects=subtable_objects)
    return output


def html_table_with_subtables(output, table_object = None, subtable_objects = None, next_function = None)
	addition += html_table(output, table_object=table_object, subtable_objects=subtable_objects, next_function=html_subtables)
	# todo: log additions
	output += addition
	return output


def html_subtables(output, subtable_objects = None, next_function = None):
	if subtable_objects:
		for subtable in subtable_objects:
			output += html_table(output, table_object = subtable, next_function = None):
	# todo: log messages
	return output


def html_table(output, table_object = None, next_function = None):
	items = session.query(table_object)
	item_headers = items.column_descriptions
	for header in item_headers:
		output += "<th>{}</th>".format(header)
	for item in items:
		# todo: generalize 
    	for column in items.__table__.columns.keys()
			column_data = getattr(item, header)
			output += "<td>{}</td>".format(column_data)
    	output += "</table>"
    	output += "<br>"
    	if next_function:
    		# todo: log messages
    		return next_function(output, args*, kwargs**)
	# todo: log messages
	return output


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)