from flask import Flask, request, redirect, render_template, url_for, flash, jsonify
app = Flask(__name__)

from flask import session as login_session
import random, string
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query

from config import SQL_COMMAND
from database_setup import Restaurant, Base, MenuItem

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

engine = create_engine(SQL_COMMAND)
Base.metadata.bind = engine
DBSessionMaker = sessionmaker(bind=engine)
session = DBSessionMaker()
verified = False


@app.route('/gconnect', methods=['POST']) 
def gconnect():
    print('login_session:{}'.format(login_session))
    if request.args.get('state') != login_session
    response = make_response(json.dumps('Invalid state parameter!', 401))
    response.headers['Content-Type'] = 'application/json'
    return response



@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state']=state
    oauth_dict = get_asset_oauth()
    oauth_client_id = oauth_dict['client_id']
    return render_template('login.html', oauth_client_id=oauth_client_id,state=STATE)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET'])
def restaurants_redirect():
    return redirect("/restaurant")

@app.route('/restaurant/', methods=['GET'])
@app.route('/restaurant', methods=['GET'])
def restaurant_index():
    restaurant_count = session.query(Restaurant).count()
    print(restaurant_count)
    limit = 10
    restaurants = session.query(Restaurant).order_by(Restaurant.last_time.desc()).limit(limit)
    return render_template('index.html', verified = verified, restaurants=restaurants)

@app.route('/api/restaurant', methods=['GET'])
def api_all_restaurants():
    restaurants = session.query(Restaurant)
    Restaurants=[i.serialize for i in restaurants]
    return jsonify(Restaurants)


@app.route('/restaurant/add', methods=['GET','POST'])
def add_restaurant():
    if request.method == 'POST':
        name = request.form['restaurant_name']
        restaurant = Restaurant()
        restaurant.name = name
        session.add(restaurant)
        session.commit()
        flash("new restaurant created")
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
    
@app.route('/api/restaurant/<int:restaurant_id>/menu/', methods=['GET'])
def api_restaurant_menu(restaurant_id):
    restaurant_key = 'menu'
    print('restaurant_key: {}'.format(restaurant_key))
    restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_id).one_or_none()
    if restaurant is None:
        return redirect(url_for(page_not_found))
    else:
        restaurant_json = restaurant.serialize
        print('restaurant_json: {}'.format(restaurant_json))
        if restaurant_key in restaurant_json.keys():
            return jsonify({restaurant_key: restaurant_json.get(restaurant_key)})
        else:
            return redirect(url_for(page_not_found))

@app.route('/api/restaurant/<int:restaurant_id>/menu/<int:menu_item_id>', methods=['GET'])
def api_restaurant_menu_item(restaurant_id, menu_item_id):
    menu_item = menu_items = session.query(MenuItem).filter(MenuItem.id == menu_item_id).one_or_none()
    if menu_item is None:
        return redirect(url_for(page_not_found))
    else:
        menu_item_json = menu_item.serialize
        return jsonify(menu_item_json)

@app.route('/api/restaurant/<int:restaurant_id>/menu/<int:menu_item_id>/<string:item_key>', methods=['GET'])
def api_restaurant_menu_item_details(restaurant_id, menu_item_id, item_key):
    menu_item = menu_items = session.query(MenuItem).filter(MenuItem.id == menu_item_id).one_or_none()
    if menu_item is None:
        return redirect(url_for(page_not_found))
    else:
        menu_item_json = menu_item.serialize
        if item_key in menu_item_json.keys():
            return jsonify({item_key: menu_item_json.get(item_key)})
    return redirect(url_for(page_not_found))


@app.route('/api/restaurant/<int:restaurant_id>/<string:restaurant_key>', methods=['GET'])
def api_restaurant_item(restaurant_id, restaurant_key):
    print('restaurant_key: {}'.format(restaurant_key))
    restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_id).one_or_none()
    if restaurant is None:
        return redirect(url_for(page_not_found))
    else:
        restaurant_json = restaurant.serialize
        if restaurant_key in restaurant_json.keys():
            return jsonify({restaurant_key: restaurant_json.get(restaurant_key)})
        else:
            return redirect(url_for(page_not_found))

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def edit_restaurant(restaurant_id):
    if verified is True:
        if request.method == 'POST':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                name = request.form['restaurant_name']
                restaurant.name = name
            session.commit()
            flash("restaurant edited")
        elif request.method == 'GET':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                return render_template('edit_category.html', verified = verified, restaurant=restaurant)
    return redirect("/restaurant")


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
                flash("restaurant deleted")
        elif request.method == 'GET':
            restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
            for restaurant in restaurants:
                return render_template('delete_category.html', verified = verified, restaurant=restaurant)
    return redirect("/restaurant")


@app.route('/restaurant/<int:restaurant_id>/menu/add', methods=['GET','POST'])
def restaurant_add_menu_items(restaurant_id):
    if verified is True:
        restaurants = session.query(Restaurant).filter(Restaurant.id==restaurant_id)
        for restaurant in restaurants:
            if request.method == 'POST':
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
                flash("new item created")
            elif request.method == 'GET':
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
                    flash("item edited")
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
            flash("item deleted")
    return redirect( "/restaurant/{}/menu".format(restaurant.id))


def get_asset_oauth():
    file_path = './assets/oauth.json'
    with open(file_path) as json_file:
        oauth_dict = json.load(json_file)
    return oauth_dict


if __name__ == '__main__':
    verified = True
    app.secret_key = 'super_secret'
    app.run(host='0.0.0.0', port=5000)