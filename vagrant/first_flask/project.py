from flask import Flask, request, redirect, render_template, url_for
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

verified = False

@app.route('/', methods=['GET'])
def restaurants_redirect():
    return redirect("/restaurant")

@app.route('/restaurant/', methods=['GET'])
@app.route('/restaurant', methods=['GET'])
def restaurants():
    restaurant_count = session.query(Restaurant).count()
    print(restaurant_count)
    limit = 10
    restaurants = session.query(Restaurant).order_by(Restaurant.last_time.desc()).limit(limit)
    return render_template('index.html', verified = verified, restaurants=restaurants)


@app.route('/restaurant/add', methods=['GET','POST'])
def add_restaurant():
    if request.method == 'POST':
        name = request.form['restaurant_name']
        restaurant = Restaurant()
        restaurant.name = name
        session.add(restaurant)
        session.commit()
        return redirect("/restaurant")
    elif request.method == 'GET':
        return render_template('add_category.html', verified = verified)


@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    if request.method == 'GET':
        restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
        menu_items = session.query(MenuItem).filter(MenuItem.restaurant_id==restaurant_id).order_by(MenuItem.course)
        for restaurant in restaurants:
            return render_template('category.html', verified = verified, restaurant=restaurant, menu_items=menu_items)
    

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def edit_restaurant(restaurant_id):
    
    if verified is True:
        if request.method == 'POST':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                name = request.form['restaurant_name']
                restaurant.name = name
            session.commit()
        elif request.method == 'GET':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                return render_template('edit_category.html', verified = verified, restaurant=restaurant)
    return redirect("/restaurant")


def html_edit_restaurant(restaurant,verified):
    if verified is True:
        return '''
            <h2>Edit Restaurant:{} (#{})</h2> 
            <form method="post">
                <p>Name:<input type=text name=restaurant_name>
                <p><input type=submit value=Submit>
            </form>
            <p><a href="/restaurant/{}/menu">To Menu</a><p>
            <p><a href="/restaurant/{}/menu/add">Add Menu Items</a><p>
            <p><a href="/restaurant">Back to Restaurants</a><p>
        '''.format(restaurant.name, restaurant.id, restaurant.id, restaurant.id)
    else:
        return redirect("/restaurant/{}/menu".format(restaurant.id))


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def delete_restaurant(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    if verified is True:
        for restaurant in restaurants:
            if request.method == 'POST':
                menu_items = session.query(MenuItem).filter(MenuItem.restaurant_id==restaurant_id)
                for menu_item in menu_items:
                    session.delete(menu_item)
                session.delete(restaurant)
                session.commit()
            elif request.method == 'GET':
                main_path = '/restaurant'
                output = '<h1><a href="{}"> Restaurant Listings </a></h1>'.format(main_path)
                add_content = html_delete_restaurant(restaurant)
                output += add_content
                return output
    return redirect("/restaurant".format(restaurant.id))


def html_delete_restaurant(restaurant):
    return '''
        <h2>Delete Restaurant:{}</h2> 
        <form method="post">
            <p><input type=submit value=Confirm>
        </form>
        <p><a href="/restaurant/{}/menu">To Menu</a><p>
        <p><a href="/restaurant">Back to Restaurants</a><p>
    '''.format(restaurant.name, restaurant.id)


@app.route('/restaurant/<int:restaurant_id>/menu/add', methods=['GET','POST'])
def restaurant_add_menu_items(restaurant_id):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    if verified is True:
        if request.method == 'POST':
            for restaurant in restaurants:
                menu_item = MenuItem()
                menu_item.restaurant = restaurant
                if request.form.get('item_name','') != '':
                    menu_item.name = request.form['item_name']
                if request.form.get('item_description','') != '':
                    menu_item.description = request.form['item_description']
                if request.form.get('item_price','') != '':
                    menu_item.price = request.form['item_price']
                if request.form.get('item_course','') != '':
                    menu_item.course = request.form['item_course']
                session.add(menu_item)
            session.commit()
        if request.method == 'GET':
            main_path = '/restaurant'
            output = '<h1><a href="{}"> Restaurant Listings </a></h1>'.format(main_path)
            add_content = site_restaurant_add_menu_item(restaurant_id, verified)
            output += add_content
            return output
    return redirect("/restaurant/{}/menu".format(restaurant_id))


def site_restaurant_add_menu_item(restaurant_id, verified):
    restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
    for restaurant in restaurants:
        menu_items = session.query(MenuItem).filter(MenuItem.restaurant_id==restaurant_id)
        for menu_item in menu_items:
            output = html_add_menu_items(restaurant, menu_item, verified)
    return output


def html_add_menu_items(restaurant, menu_item, verified):
    if verified is True:
        output = '''
            <h2>Restaurant:{}</h2>
            <h2>Add Menu Item:</h2> 
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
                    restaurant.id)
        return output
    else:
        menu_path = "/restaurant/{}/menu".format(restaurant.id)
        return redirect(menu_path)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_item_id>/edit', methods=['GET','POST'])
def edit_menu_item(restaurant_id, menu_item_id):
    if verified is True: 
        restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
        menu_items = session.query(MenuItem).filter(MenuItem.id == menu_item_id)
        for restaurant in restaurants:
            for menu_item in menu_items:
                if request.method == 'POST':
                    menu_item.restaurant = restaurant
                    if request.form.get('item_name','') != '':
                        menu_item.name = request.form['item_name']
                    if request.form.get('item_description','') != '':
                        menu_item.description = request.form['item_description']
                    if request.form.get('item_price','') != '':
                        menu_item.price = request.form['item_price']
                    if request.form.get('item_course','') != '':
                        menu_item.course = request.form['item_course']
                    session.commit()
                if request.method == 'GET':
                    main_path = '/restaurant'
                    output = '<h1><a href="{}"> Restaurant Listings </a></h1>'.format(main_path)
                    add_content = html_edit_menu_items(restaurant, menu_item)
                    output += add_content
                    return output
    menu_path = "/restaurant/{}/menu".format(restaurant.id)
    return redirect(menu_path)


def html_edit_menu_items(restaurant, menu_item):
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
    
@app.route('/restaurant/<int:restaurant_id>/<int:menu_item_id>/delete', methods=['GET','POST'])
def delete_menu_items(restaurant_id, menu_item_id):
    if verified is True:
        restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
        menu_items = session.query(MenuItem).filter(MenuItem.id == menu_item_id)
        for restaurant in restaurants:
            for menu_item in menu_items:   
                if request.method == 'POST':
                    session.delete(menu_item)
                elif request.method == 'GET':
                    main_path = '/restaurant'
                    output = '<h1><a href="{}"> Restaurant Listings </a></h1>'.format(main_path)
                    add_content = html_delete_menu_item(restaurant, menu_item)
                    output += add_content
                    return output
            session.commit()
    menu_path = "/restaurant/{}/menu".format(restaurant.id)
    return redirect(menu_path)


def html_delete_menu_item(restaurant, menu_item):
    return '''
        <h2>Confirm Menu Item Delete:{}</h2> 
        <form method="post">
            <p><input type=submit value=Confirm>
        </form>
        <p><a href="/restaurant/{}/menu">To Menu</a><p>
        <p><a href="/restaurant">Back to Restaurants</a><p>
    '''.format(menu_item.name, restaurant.id)


if __name__ == '__main__':
    verified = True
    app.run(host='0.0.0.0', port=5000)