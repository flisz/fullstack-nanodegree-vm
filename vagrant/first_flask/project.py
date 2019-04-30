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
    if verified is True:
        if request.method == 'POST':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                menu_items = session.query(MenuItem).filter(MenuItem.restaurant_id==restaurant_id)
                for menu_item in menu_items:
                    session.delete(menu_item)
                session.delete(restaurant)
                session.commit()
        elif request.method == 'GET':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                return render_template('delete_category.html', verified = verified, restaurant=restaurant)
    return redirect("/restaurant")


@app.route('/restaurant/<int:restaurant_id>/menu/add', methods=['GET','POST'])
def restaurant_add_menu_items(restaurant_id):
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
        elif request.method == 'GET':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                return render_template('add_item.html', restaurant=restaurant)
    return redirect("/restaurant/{}/menu".format(restaurant_id))


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
                elif request.method == 'GET':
                    return render_template('edit_item.html', restaurant = restaurant, menu_item = menu_item)
    return redirect("/restaurant/{}/menu".format(restaurant.id))

    
@app.route('/restaurant/<int:restaurant_id>/<int:menu_item_id>/delete', methods=['GET','POST'])
def delete_menu_items(restaurant_id, menu_item_id):
    if verified is True:
        restaurants = session.query(Restaurant).filter(Restaurant.id == restaurant_id)
        menu_items = session.query(MenuItem).filter(MenuItem.id == menu_item_id)
        for restaurant in restaurants:
            for menu_item in menu_items:   
                if request.method == 'POST':
                    session.delete(menu_item)
                elif request.method == 'GET':
                    return render_template('delete_item.html', restaurant = restaurant, menu_item = menu_item)
            session.commit()
    return redirect( "/restaurant/{}/menu".format(restaurant.id))


if __name__ == '__main__':
    verified = True
    app.run(host='0.0.0.0', port=5000)