from flask import Flask, request, redirect, render_template, url_for, flash, jsonify
from flask import make_response
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
import google.auth.transport.requests
import requests 
import httplib2


# need to generate client_secrets and place in assets folder
CLIENT_ID = json.loads(open('assets/client_secrets.json','r').read())['web']['client_id']


def get_asset_oauth():
    # need to generate oauth on XX similar to assets/oauth_template.json and place in assets folder
    file_path = './assets/oauth.json'
    with open(file_path) as json_file:
        oauth_dict = json.load(json_file)
    return oauth_dict


@app.route('/google-connect', methods=['POST']) 
def google_connect():
    login_state = login_session.get('state')
    print('login_session:{}'.format(login_state))
    data = json.loads(request.data.decode("utf-8"))
    print('request.data={}'.format(data))
    response_state = request.args.get('state')
    print('response_state:{}'.format(response_state))
    if response_state != login_state:
        # if login_session is not valid end-point
        print('state does not match!')
        response = make_response(json.dumps('Invalid state parameter!'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = data.get('id_token')
    print('access_token:{}'.format(access_token))
    print("CLIENT_ID:{}".format(CLIENT_ID))
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
    '''
    url = ('https://oauth2.googleapis.com/tokeninfo?id_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1].decode("utf-8"))
    print('result:{}'.format(result))
    result_error = result.get('error')
    if result_error is not None:
        response = make_response(json.dumps(result_error), 500)
        response.headers['Content-Type'] = 'application/json'

    # verify access is for intended user
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        google_auth_request = google.auth.transport.requests.Request()
        print("google_auth_request:{}".format(google_auth_request))
        id_info = id_token.verify_oauth2_token(access_token, google_auth_request, CLIENT_ID)
        print("id_info:{}".format(id_info))

        # Or, if multiple clients access the backend server:
        # id_info = id_token.verify_oauth2_token(token, google_auth_request)
        # if id_info['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if id_info['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        user_id = id_info['sub']
        print("user_id:{}".format(user_id))
    except ValueError:
        
        print("Invalid Token!!!")
        pass

    if result['sub'] != user_id:
        authentication_error_message = "Token's user ID does not match given user ID"
        response = make_response(json.dumps(authentication_error_message), 401)
        response.headers['Content-Type'] = 'application/json'
        print(authentication_error_message)
        return response
    if result['azp'] != CLIENT_ID:
        authentication_error_message = "Token's client ID does not match app's"
        response = make_response(json.dumps(authentication_error_message), 401)
        print(authentication_error_message)
        return response
    
    stored_user_id = login_session.get('user_id')
    stored_access_token = login_session.get('access_token')
    if stored_access_token is not None and user_id == stored_user_id:
        # user is already logged in
        response = make_response(json.dumps('current user already logged in'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # new user just logged in. save in session for future use
    login_session['access_token'] = access_token
    login_session['user_id'] = user_id
    login_session['username'] = id_info.get('name')
    login_session['picture'] = id_info.get('picture')
    login_session['email'] = id_info.get('email')
    print("new login_session started: {}".format(login_session))
    return redirect("/login")

@app.route('/google-disconnect', methods=['POST']) 
def google_disconnect():
    login_state = login_session.get('state')
    print('login_session:{}'.format(login_state))
    data = json.loads(request.data.decode("utf-8"))
    print('request.data={}'.format(data))
    response_state = request.args.get('state')
    print('response_state:{}'.format(response_state))
    if response_state != login_state:
        # if login_session is not valid end-point
        print('state does not match! (invalid disconnect request?)')
        response = make_response(json.dumps('Invalid state parameter!'), 401)
        response.headers['Content-Type'] = 'application/json'
        new_login_session()
        return response
    else: 
        new_login_session()
        return redirect("/login")

def new_login_session():
    for key in list(login_session.keys()):
        login_session.pop(key)
    print("login_session cleared: {}".format(login_session))
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state']=state
    oauth_dict = get_asset_oauth()
    login_session['oauth_client_id'] = oauth_dict['client_id'] 


@app.route('/login', methods=['GET', 'POST'])
def show_login():
    if request.method == 'POST':
        print("request.form:{}".format(request.form))
        new_login_session()
        return redirect("/login")
    elif request.method == 'GET':
        if login_session.get('access_token'):
            print('User is logged into login_session: {}!'.format(login_session))
        else:
            new_login_session()
            print('No user is logged into login_session: {}!'.format(login_session))
        # in this case, server is the client for id provided by oauth service (google)
        return render_template('login.html', login_session=login_session)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', login_session=login_session, e=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', login_session=login_session, e=e), 500

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





if __name__ == '__main__':
    verified = True
    app.secret_key = 'super_secret'
    app.run(host='0.0.0.0', port=5000)