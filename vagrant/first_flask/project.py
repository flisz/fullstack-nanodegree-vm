from flask import Flask, request, redirect, render_template, url_for, flash, jsonify
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

from flask import session as login_session
import random, string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from google.oauth2 import id_token
from google.auth.transport import requests

import httplib2
from flask import make_response
import requests
# need to generate client_secrets and place in assets folder
CLIENT_ID = json.loads(open('assets/client_secrets.json','r').read())['web']['client_id']


@app.route('/gconnect', methods=['POST']) 
def gconnect():
    login_state = login_session.get('state')
    print('login_session:{}'.format(login_state))
    data = json.loads(request.data.decode("utf-8"))
    print('request.data={}'.format(data))
    response_state = request.args.get('state')
    print('response_state:{}'.format(response_state))
    if response_state != login_state:
        # if login_session is not valid end-point
        print('state does not match!')
        response = make_response(json.dumps('Invalid state parameter!', 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    token = data.get('id_token')
    print('token:{}'.format(token))
    '''try:
        # make credentials from auth code
        oauth_flow = flow_from_clientsecrets('assets/client_secrets.json', scope=[])
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print("credentials: {}".format(credentials))
    except FlowExchangeError:
        print('FlowExchangeError')
        response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1].decode("utf-8"))
    print('result:{}'.format(result))
    result_error = result.get('error')
    if result_error is not None:
        response = make_response(json.dumps(result_error), 500)
        response.headers['Content-Type'] = 'application/json' '''    
    # verify access is for intended user
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        verify_id_token_request = requests.Request()
        idinfo = id_token.verify_oauth2_token(token, verify_id_token_request, CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        user_id = idinfo['sub']
        print("user_id:{}".format(user_id))
    except ValueError:
        print("Invalid Token!!!")
        pass
    # user_id = credentials.id_token['sub']
    if result != user_id:
        response = make_response(json.dumps("Token's user ID does not match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        print("user_id bad")
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's"))
        print("client_id bad")
    #user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('current user already logged in'), 200)
        response.headers['Content-Type'] = 'application/json'
    # store access token in session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id
    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    print('\n'.join(data.split(',')))
    login_session['username'] = data.get('name')
    login_session['picture'] = data.get('picture')
    login_session['email'] = data.get('email')
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as {}".format(login_session['username']))
    print("done! wooo")
    return output


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state']=state
    oauth_dict = get_asset_oauth()
    oauth_client_id = oauth_dict['client_id']
    return render_template('login.html', oauth_client_id=oauth_client_id,STATE=state)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html',e=e), 404

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