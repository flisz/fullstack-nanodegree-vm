from flask import Flask, request, redirect
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
def restaurants_redirect():
    return redirect("restaurant")


@app.route('/restaurant', methods=['GET'])
def restaurants():
    restaurants = session.query(Restaurant)
    verified = True
    output = site_restaurant(verified)    
    return output


def site_restaurant(verified = None):
    restaurants = session.query(Restaurant)
    restaurant_headers = None
    for restaurant in restaurants:
        add_restaurant_table = html_table_restaurant(restaurants = restaurants, verified = verified, restaurant_headers = restaurant_headers)
        output = ''
        output += '<h3><a href="/restaurant/add">Add Restaurant</a></h3>' + add_restaurant_table      

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

    output += "<table>"
    output += "<tr>"
    for header in restaurant_headers:
        output += "<th>{}</th>".format(header)
    output += '<th>Menu</th>'
    if verified is True:
        output += '<th>Edit</th>'
        output += '<th>Delete</th>'
    output += "</tr>"
    output += "<tr>"
    for restaurant in restaurants:
        for header in restaurant_headers:
            column_data = getattr(restaurant, header)
            output += "<td>{}</td>".format(column_data)
        menu_path = "/restaurant/{}/menu".format(restaurant.id)
        output += '<td><a href="{}">Menu</a></td>'.format(menu_path)
        if verified is True:
            edit_path = "/restaurant/{}/edit".format(restaurant.id)
            delete_path = "/restaurant/{}/delete".format(restaurant.id)
            output += '<td><a href="{}">Edit</a></td>'.format(edit_path)
            output += '<td><a href="{}">Delete</a></td>'.format(delete_path)
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
    if verified is True: 
        if request.method == 'POST':
            name = request.form['restaurant_name']
            restaurant = Restaurant()
            restaurant.name = name
            session.add(restaurant)
            session.commit()
            return redirect("/restaurant")
        return '''
            <h2>Add New Restaurant:</h2> 
            <form method="post">
                <p>Name:<input type=text name=restaurant_name>
                <p><input type=submit value=Add>
            </form>
            <p><a href="/restaurant">Back</a><p>
        '''
    else:
        return redirect("/restaurant")

@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    print(restaurant_id)
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    menu_items = session.query(MenuItem).filter(MenuItem.restaurant_id==restaurant_id)
    verified = True
    menu_item_headers = None
    output = site_restaurants_with_menu_items(restaurants = restaurants, 
                                              menu_items = menu_items, menu_item_headers = menu_item_headers, 
                                              verified = verified)
    return output


def site_restaurants_with_menu_items(output=None, verified = None,
                                     restaurants = None,  
                                     menu_items = None, menu_item_headers = None):
        output = ''
        for restaurant in restaurants:
            output += "<h2>{}: (#{})<h2>".format(restaurant.name, restaurant.id)
            if verified is True: 
                '<h4><a href="/restaurant/{}/menu/add">Add Menu Item</a></h4>'.format(restaurant.id)
            output += "<h3>Menu:<h3>"
            add_menu_item_table = html_table_menu_items(verified = verified,
                          restaurant = restaurant, 
                          menu_items = menu_items, menu_item_headers = menu_item_headers)
            output += add_menu_item_table        
        return output


def html_table_menu_items(verified = None,
                          restaurant = None, 
                          menu_items = None, menu_item_headers = None):
    if menu_item_headers is None:
        menu_item_headers = MenuItem.__table__.columns.keys()

    output = "<table>"
    output += "<tr>"
    for header in menu_item_headers:
        output += "<th>{}</th>".format(header)
    if verified is True:
        output += '<th>Edit</th>'
        output += '<th>Delete</th>'
    output += "</tr>"
    for menu_item in menu_items:
        output += "<tr>"
        for header in menu_item_headers:
            column_data = getattr(menu_item, header)
            output += "<td>{}</td>".format(column_data)
        if verified is True:
            edit_path = "/restaurant/{}/{}/edit".format(restaurant.id,menu_item.id)
            delete_path = "/restaurant/{}/{}/delete".format(restaurant.id,menu_item.id)
            output += '<td><a href="{}">Edit</a></td>'.format(edit_path)
            output += '<td><a href="{}">Delete</a></td>'.format(delete_path)
        output += "</tr>"
    output += "</table>"
    output += "<br>"
    return output


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def edit_restaurant(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    verified = True
    if request.method == 'POST':
        if verified is True:
            name = request.form['restaurant_name']
            for restaruant in restaruants:
                restaurant = session.query(Restaruant).filter(Restaurant.id==restaurant_id)
                restaurant.name = name
            session.commit()
        return redirect("/restaurant")
    else:
        output = html_edit_restaurant(restaurant_id, verified)
        return output


def html_edit_restaurant(restaruant,verified):
    if verified is True:
        return '''
            <h2>Edit Restaurant:{}</h2> 
            <form method="post">
                <p>Name:<input type=text name=restaurant_name>
                <p><input type=submit value=Submit>
            </form>
            <p><a href="/restaurant/{}/menu">to Menu</a><p>
            <p><a href="/restaurant">Back to Restaurants</a><p>
        '''
    else:
        return redirect("/restaurant")

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def delete_restaurant(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    verified = True
    output = site_delete_restaurants(restaurant_id, verified)
    return output


def site_delete_restaurants(restaurant_id, verified):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    verified = True
    if request.method == 'POST':
        if verified is True:
            for restaruant in restaruants:
                restaurant = session.delete(restaurant)
            session.commit()
        return redirect("/restaurant")
    else:
        output = html_delete_restaurant(restaurant_id, verified)
        return output


def html_delete_restaurant(output = None, verified = None, 
                          restaurant = None):
    if verified is True:
        return '''
            <h2>Delete Restaurant:{}</h2> 
            <form method="post">
                <p><input type=submit value=Confirm>
            </form>
            <p><a href="/restaurant/{}/menu">to Menu</a><p>
            <p><a href="/restaurant">Back to Restaurants</a><p>
        '''.format(restaurant.name,restaurant.id)
    else:
        return redirect("/restaurant")

@app.route('/restaurant/<int:restaurant_id>/add_menu_items', methods=['GET','POST'])
def restaurant_add_menu_items(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    verified = True
    output = site_restaurant_add_menu_item(restaurant)
    return output


def site_restaurant_add_menu_item(restaurant_id, verified):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    menu_items = session.query(MenuItem).filter(MenuItem.id==menu_item_id)
    for restaurant in restaurants:
        for menu_item in menu_items:
            output = html_add_menu_items(restaurant, menu_item, verified)
    return output


def html_add_menu_items(restaurant, menu_item, output = None, verified = None):
    if verified == True:
        output = '''
            <h2>Restaurant:{}</h2>
            <h2>Add Menu Item:{}</h2> 
            <form method="post">
                <table>
                <tr><td>Name:</td><td><input type=text name=item_name></td></tr>
                <tr><td>Course</td><td><input type=text name=item_course></td></tr>
                <tr><td>Price:</td><td><input type=text name=item_price></td></tr>
                <tr><td>Description:</td><td><input type=text name=item_description></td></tr>
                </table>
                <input type=submit value=Accept>
            </form>
            <p><a href="/restaurant/{}/menu">Back to Menu</a><p>
            <p><a href="/restaurant">Back to Restaurants</a><p>
        '''.format(restaurant.name,
                    menu_item.name,
                    menu_item.name,
                    menu_item.course, 
                    menu_item.price,
                    menu_item.description,
                    restaurant.id)
        return output
    else:
        menu_path = "/restaurant/{}/menu".format(restaurant.id)
        return redirect(menu_path)


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
            <p><a href="/restaurant/{}/menu">Back to Menu</a><p>
            <p><a href="/restaurant">Back to Restaurants</a><p>
        '''.format(restaurant.name,
                    menu_item.name,
                    menu_item.name,
                    menu_item.course, 
                    menu_item.price,
                    menu_item.description,
                    restaurant.id)
        return output
    else:
        menu_path = "/restaurant/{}/menu".format(restaurant.id)
        return redirect(menu_path)

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