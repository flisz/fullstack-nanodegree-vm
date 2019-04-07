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
    ######### TABLE -------------
    output += "<table>"
    for header in restaurants_headers:
    		output += "<th>{}</th>".format(header)
    for restaurant in restaurants:
    	# todo: generalize 
    	for column in restaurants.__table__.columns.keys()
			column_data = getattr(restaurant, header)
			output += "<td>{}</td>".format(column_data)
    	output += "</table>"
    	output += "<br>"
    	######### TABLE -------------
    	######### SUBTABLE -------------
    	menu_items = session.query(MenuItem)
    	menu_items_headers = menu_items.column_descriptions
    	for header in restaurants_headers:
    		output += "<th>{}</th>".format(header)
    	for item in items:
    		# todo: generalize 
	    	for column in restaurants.__table__.columns.keys()
				column_data = getattr(item, header)
				output += "<td>{}</td>".format(column_data)
	    	output += "</table>"
	    	output += "<br>"

    	for header in menu_items_headers:
    		output += "<table>"
    		output += "<th>{}</th>".format(header)
		for menu_item in menu_items:
			output += "<td>{}</td>".format(restaurant.id)
			output += "<td>{}</td>".format(restaurant.name)
    		output += "</table>"
    		output += "<br>"
    	######### SUBTABLE -------------


    	restaurants = session.query(Restaurant)
    	for menu_item in 
    	for header in restaurants_headers:
    		output += "<th>{}</th>".format(header)
    


    return "Hello World"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)