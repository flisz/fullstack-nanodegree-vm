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
    # Main Table:
    output = html_restaurants()
    return output

def html_restaurants():
    restaurants = session.query(Restaurant)
    restaurant_headers = Restaurant.__table__.columns.keys()
    output = ''
    for restaurant in restaurants:
        # todo: generalize 
        
        print("restaurant_headers: {}".format(restaurant_headers))
        output += "<table>"
        output += "<tr>"
        for header in restaurant_headers:
            output += "<th>{}</th>".format(header)
        output += "</tr>"
        output += "<tr>"
        for header in restaurant_headers:
            column_data = getattr(restaurant, header)
            output += "<td>{}</td>".format(column_data)
        output += "</tr>"
        output += "</table>"
        output += "<br>"
        addition = html_menu_items(restaurant)
        output += addition
                
    # todo: log messages
    return output

def html_menu_items(restaurant):
    menu_items = session.query(MenuItem).filter(MenuItem.restaurant == restaurant)
    item_headers = MenuItem.__table__.columns.keys()
    output = "<table>"
    output += "<tr>"
    for header in item_headers:
        output += "<th>{}</th>".format(header)
    output += "</tr>"
    for item in menu_items:
        # todo: generalize 
        item_headers = MenuItem.__table__.columns.keys()
        print("item_headers: {}".format(item_headers))
        output += "<tr>"
        for header in item_headers:
            column_data = getattr(item, header)
            output += "<td>{}</td>".format(column_data)
        output += "</tr>"
    output += "</table>"
    output += "<br>"
    return output
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)