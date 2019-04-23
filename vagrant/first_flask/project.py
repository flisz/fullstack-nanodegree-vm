from flask import Flask, request
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
@app.route('/restaurant', methods=['GET'])
def restaurants():
    restaurants = session.query(Restaurant)
    verified = True
    output = site_restaurant(verified)    
    return output


def site_restaurant(verified = None):
    restaurants = session.query(Restaurant)
    for restaurant in restaurants:
        add_restaurant = html_restaurant(restaurants, verified = verified, restaurant_headers = restaurant_headers)
        output += add_restaurant        
    return output


def html_table_restaurant(output = None, verified = None, 
                          restaurants = None, restaurant_headers = None, restaurant_id = None,  
                          menu_items = None, menu_item_headers = None, menu_item_id = None):
    if output is None: 
        output = ''
    if restaurants is None:
        restaurants = session.query(Restaurant)
    if restaurant_headers is None:
        restaurant_headers = Restaurant.__table__.columns.keys()

    print("restaurant_headers: {}".format(restaurant_headers))
    output += "<table>"
    output += "<tr>"
    for header in restaurant_headers:
        output += "<th>{}</th>".format(header)
    if verified is True:
        output += '<th>Edit</th>'
        output += '<th>Delete</th>'
    output += "</tr>"
    output += "<tr>"
    for header in restaurant_headers:
        column_data = getattr(restaurant, header)
        output += "<td>{}</td>".format(column_data)
        if verified is True:
            output += '<td><a href="{}"}>Edit</a></td>'.format(edit_path)
            output += '<td><a href="{}"}>Delete</a></td>'.format(delete_path)
    output += "</tr>"
    output += "</table>"
    output += "<br>"
    return output


@app.route('/restaurant/add', methods=['GET','POST'])
def add_restaurant():
    verified = True
    output = site_add_restaurant(verified)    
    return output


def site_add_restaurant(verified):
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <h2>Add New Restaurant:</h2> 
        <form method="post">
            <p>Name:<input type=text name=restaurant_name>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/restaurant/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    verified = True
    restaurant_headers = None
    menu_item_headers = None
    output = site_restaurants_with_menu_items(restaurants, restaurant_headers, menu_item_headers, verified)
    return output


def site_restaurants_with_menu_items(output=None, verified = None,
                                     restaurants = None, restaurant_headers = None, restaurant_id = None,  
                                     menu_items = None, menu_item_headers = None, menu_item_id = None):
    if verified is True:
        if output is None: 
            output = ''
        if menu_item_id is None:
            if restaurant_id is not None:
                restaurants = session.query(Restaurant).filter(Restaurant.id == restaurant_id)
            if restaurants is None:
                restaurants = session.query(Restaurant)
            for restaurant in restaurants:
                # todo: generalize 
                add_restaurant = html_table_restaurant(restaurant, restaurant_headers = restaurant_headers)
                menu_items = session.query(MenuItem).filter(MenuItem.restaurant == restaurant)
                add_menu_items = html_table_menu_items(restaurants = restaurant, menu_item_headers = menu_item_headers)
                output += add_restaurant + add_menu_items        
        else:  # if menu_item_id is not None: 
            menu_items = session.query(MenuItem).filter(MenuItem.id == menu_item_id)
            if restaurant_id is None or menu_item.restaurant_id == restaurant_id:
                restaurants = session.query(Restaurant).filter(Restaurant.id == menu_item.restaurant_id)
            else:  # restaurant_id is not None
                raise ValueError("resturant_id:{} and menu_item.resturant_id:{} do not match")
            for restaurant in restaurants:
                output += "<h2>{}: (#{})<h2>".format(restaurant.name, restaurant.id)
                add_restaurant = html_table_restaurant(restaurants = restaurant, restaurant_headers = restaurant_headers)
                output += "<h2>Menu:<h2>"
                add_menu_items = html_table_menu_items(restaurants = restaurant, menu_items = menu_items, menu_item_headers = menu_item_headers)
                output += add_restaurant + ad_menu_items         
        return output


def html_table_menu_items(verified = None,
                          restaurants = None, 
                          menu_items = None, menu_item_headers = None):
    if restaurants is None:
        restaurants = session.query(Restaurant)
    if menu_items is None:
        for restaurant in restaurants:
            menu_items = session.query(MenuItem).filter(MenuItem.restaurant == restaurant)
    if menu_item_headers is None:
        menu_item_headers = MenuItem.__table__.columns.keys()

    output = "<table>"
    output += "<tr>"
    for header in item_headers:
        output += "<th>{}</th>".format(header)
    if verified is True:
        output += '<th>Edit</th>'
        output += '<th>Delete</th>'
    output += "</tr>"
    for item in menu_items:
        # todo: generalize 
        item_headers = MenuItem.__table__.columns.keys()
        print("item_headers: {}".format(item_headers))
        output += "<tr>"
        for header in item_headers:
            column_data = getattr(item, header)
            output += "<td>{}</td>".format(column_data)
        if verified is True:
            output += '<td><a href="{}"}>Edit</a></td>'.format(edit_path)
            output += '<td><a href="{}"}>Delete</a></td>'.format(delete_path)
        output += "</tr>"
    output += "</table>"
    output += "<br>"
    return output


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def edit_restaurant(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    output = site_edit_restaurants(restaurant_id, verified)
    return output


def site_edit_restaurants(restaurant_id, verified):
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))


def html_edit_restaurant(output = None, verified = None, 
                          restaurants = None, restaurant_headers = None, restaurant_id = None,  
                          menu_items = None, menu_item_headers = None, menu_item_id = None):
    
    return '''
        <h2>Add New Restaurant:</h2> 
        <form method="post">
            <p>Name:<input type=text name=restaurant_name>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def delete_restaurant(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    verified = True
    output = site_delete_restaurants(restaurant_id, verified)
    return output


def site_delete_restaurants(restaurant_id, verified):
    pass


def html_delete_restaurant(output = None, verified = None, 
                          restaurants = None, restaurant_headers = None, restaurant_id = None,  
                          menu_items = None, menu_item_headers = None, menu_item_id = None):
    pass

@app.route('/restaurant/<int:restaurant_id>/add_menu_items', methods=['GET','POST'])
def restaurant_add_menu_items(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    verified = True
    output = site_restaurant_add_menu_items(restaurants,restaurant)
    return output


def site_restaurant_add_menu_items(restaurant_id, verified):
    pass


@app.route('/restaurant/<int:restaurant_id>/<int:menu_item_id>/')
def menu_item(restaurant_id, menu_item_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    menu_items = session.query(MenuItem).filter(MenuItem.id==menu_item_id)
    output = site_restaurants_with_menu_items(restaurants = restaurants, menu_items = menu_items)
    return output


@app.route('/restaurant/<int:restaurant_id>/<int:menu_item_id>/edit', methods=['GET','POST'])
def edit_menu_item(restaurant_id, menu_item_id):
    verified = True
    output = site_edit_menu_items(restaurant_id, menu_item_id, verified)
    return output


def site_edit_menu_items(restaurant_id, menu_item_id, verified):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    menu_items = session.query(MenuItem).filter(MenuItem.id==menu_item_id)
    for restaurant in restaurants:
        for menu_item in menu_items:
            output = html_edit_menu_items(restaurant, menu_item, verified)
    return output


def html_edit_menu_items(restaurant, menu_item, output = None, verified = None):
    if verified == True:
        output = '''
            <h2>Restaurant:{}</h2>
            <h2>Edit:{}</h2> 
            <form method="post">
                <table>
                <tr><td>Name:</td><td>{}</td><td><input type=text name=item_name></td></tr>
                <tr><td>Course</td><td>{}</td><td><input type=text name=item_course></td></tr>
                <tr><td>Price:</td><td>{}</td><td><input type=text name=item_price></td></tr>
                <tr><td>Description:</td><td>{}</td><td><input type=text name=item_description></td></tr>
                </table>
                <input type=submit value=Accept>
            </form>
        '''.format(restaurant.name,
                    menu_item.name,
                    menu_item.name,
                    menu_item.course, 
                    menu_item.price,
                    menu_item.description)
    return output

@app.route('/restaurant/<int:restaurant_id>/<int:menu_item_id>/delete', methods=['GET','POST'])
def delete_menu_items(restaurant_id, menu_item_id):
    verified = True
    output = site_restaurants_with_menu_items(restaurant, menu_item, verified)
    return output


def site_delete_menu_items(restaurant_id, menu_item_id, verified):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    menu_items = session.query(MenuItem).filter(MenuItem.id==menu_item_id)
    for restaurant in restaurants:
        for menu_item in menu_items:
            output = html_delete_menu_item(restaurant, menu_item, verified)
    return output


def html_delete_menu_item(restaurant_id, menu_item_id, output = None, verified = None):
    if verified == True:
        output = '''
            Menu Item: 
                <h2>Edit:{}</h2> 
                <form method="post">
                    <table>
                    <tr><td>Name:</td><td>{}</td></tr>
                    <tr><td>Course</td><td>{}</td></tr>
                    <tr><td>Price:</td><td>{}</td></tr>
                    <tr><td>Description:</td><td>{}</td></tr>
                    <tr><td>Restaurant:</td><td>{}</td></tr>
                    </table>
                    <input type=submit value=Accept>
                </form>
        '''.format(menu_item.name,
               menu_item.name,
               menu_item.course, 
               menu_item.price,
               menu_item.description,
               restaurant.name)
    return output


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)