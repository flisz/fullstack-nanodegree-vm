from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query

from config import SQL_COMMAND
from database_setup import Restaurant, Base, MenuItem

engine = create_engine(SQL_COMMAND)
Base.metadata.bind = engine
DBSessionMaker = sessionmaker(bind=engine)

# db won't be persisted into the database until you call stage.commit()
# stage.rollback() to revert all of them back to the last commit by calling

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            method = "GET"
            print("{}: {}".format(method, self.path))
            self.send_output(200, method)
        except IOError:
            self.send_error(404, "File Not Found: {}".format(self.path))

    def do_POST(self):
        try:
            method = "POST"
            print("{}: {}".format(method, self.path))
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            print("ctype:\t{}".format(ctype))
            print("pdict:\t{}".format(pdict))
            if pdict.get('boundary') is not None:
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                print("fields:\t{}".format(fields))
                if self.path.endswith('/delete?'):
                    self.restaurant_delete()
                elif self.path.endswith('/new?') and fields.get('restaurant_create_name'):
                    restaurant_create_name = fields.get('restaurant_create_name')[0].decode()
                    self.restaurant_create(restaurant_create_name)
                elif self.path.endswith('/edit?') and fields.get('restaurant_update_name'):
                    restaurant_update_name = fields.get('restaurant_update_name')[0].decode()
                    self.restaurant_update(restaurant_update_name)
            self.send_output(201, method)
        except IOError:
            self.send_error(404, "File Not Found: {}".format(self.path))

    def restaurant_delete(self):
        sp = self.path.split("/")
        if len(sp) > 3:
            path_id = sp[2]
            stage = DBSessionMaker()
            restaurants = stage.query(Restaurant).filter(Restaurant.id == path_id)
            for restaurant in restaurants:
                menu_items = stage.query(MenuItem).filter(MenuItem.restaurant == restaurant)
                for menu_item in menu_items:
                    print("DELETING:\t{}".format(menu_item.name))
                    stage.delete(menu_item)
                print("DELETING:\t{}".format(restaurant.name))
                stage.delete(restaurant)
            stage.commit()

    def restaurant_update(self, name):
        print("UPDATING: {}".format(name))
        sp = self.path.split("/")
        if len(sp) > 3:
            path_id = sp[2]
            stage = DBSessionMaker()
            restaurants = stage.query(Restaurant).filter(Restaurant.id == path_id)
            for restaurant in restaurants:
                print("UPDATING: {} TO: {}".format(restaurant.name,name))
                restaurant.name = name
            stage.commit()

    def restaurant_create(self, name):
        print("CREATE: {}".format(name))
        restaurant = Restaurant()
        restaurant.name = name
        stage = DBSessionMaker()
        stage.add(restaurant)
        stage.commit()

    def send_output(self,response,method):
        output = self.render_page(method)
        if output != '':
            self.send_response(response)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(output.encode('utf-8')) 
                    
    def render_page(self, method):
        output = ""
        sp = self.path.split("/")
        print("path_list:\t{}".format(sp))
        if sp[-1] == '' or method == "POST" or self.path.endswith("?back=Back"):
            self.send_response(303)
            if self.path.endswith("?back=Back") or method == "POST":
                self.send_header('Location', '/restaurants')
            if sp[-1] == '':
                path = '/'.join(sp[:-1])
                self.send_header('Location', '{}'.format(path))
            self.end_headers()
            return output
        output += "<html><body>"
        if self.path == "/restaurants":
            output = self.render_restaurants(output)
        else:
            if sp[1] == "restaurants":
                if len(sp) == 3:
                    if sp[2] == "new?":
                        output = self.render_restaurant_new(output)
                elif len(sp) == 4:
                    path_id = sp[2]
                    if sp[3] == "edit?":
                        output = self.render_restaurant_edit(output, path_id)
                    elif sp[3] == "delete?":
                        output = self.render_restaurant_delete(output, path_id)
        output += "</body></html>"
        return output

    def render_restaurants(self, output):
        output += "<form method = 'GET' enctype='multipart/form-data' action='restaurants/new'>"
        output += "<input type = 'submit' value = 'Create New Restaurant'></form>"
        output += "<table style='width:100%'>"
        output += "<tr>"
        output += "<th>RESTAURANT:</th>"
        output += "<th>ID:</th>"
        output += "<th>EDIT:</th>"
        output += "<th>DELETE:</th>"
        output += "</tr>"
        stage = DBSessionMaker()
        restaurants = stage.query(Restaurant)
        for restaurant in restaurants:
                output += "<tr>"
                output += "<td>{}</td>".format(restaurant.name)
                output += "<td>{}</td>".format(restaurant.id)
                #edit button
                output += "<td>"
                output += "<form method = 'GET' enctype='multipart/form-data' action='restaurants/{}/edit'>".format(restaurant.id)
                output += "<input type = 'submit' value = 'Edit'></form>"
                output += "</td>"
                #delete button
                output +="<td>"
                output += "<form method = 'GET' enctype='multipart/form-data' action='restaurants/{}/delete'>".format(restaurant.id)
                output += "<input type = 'submit' value = 'Delete'></form>"
                output += "</td>"
                output += "</tr>"
        return output

    def render_restaurant_edit(self, output, path_id):
        stage = DBSessionMaker()
        print("path_id: {}, type:{}".format(path_id,type(path_id)))
        restaurants = stage.query(Restaurant).filter(Restaurant.id == path_id)
        for restaurant in restaurants:
            output += "<h4>Edit Restaurant: {}</h4>".format(restaurant.name)
            output += "<form method = 'POST' enctype='multipart/form-data' action=''>"
            output += "<input type='text' name='restaurant_update_name'>"
            output += "<input type = 'submit' name = 'accept' value = 'Submit'></form>"
            output += "<form method = 'GET' enctype='multipart/form-data' action=''>"
            output += "<input type = 'submit' name = 'back' value = 'Back'></form>"
        return output

    def render_restaurant_delete(self, output, path_id):
        stage = DBSessionMaker()
        print("path_id: {}, type:{}".format(path_id,type(path_id)))
        restaurants = stage.query(Restaurant).filter(Restaurant.id == path_id)
        for restaurant in restaurants:
            output += "<h4>Confirm Delete Restaurant: {}</h4>".format(restaurant.name)
            output += "<form method = 'POST' enctype='multipart/form-data' action=''>"
            output += "<input type = 'submit' name = 'accept' value = 'Confirm'></form>"
            output += "<form method = 'GET' enctype='multipart/form-data' action=''>"
            output += "<input type = 'submit' name = 'back' value = 'Back'></form>"
        return output

    def render_restaurant_new(self, output):
        output += "<h4>New Restaurant:</h4>"
        output += "<form method = 'POST' enctype='multipart/form-data' action=''>"
        output += "<input type='text' name='restaurant_create_name'>"
        output += "<input type = 'submit' name = 'new' value = 'New'></form>"
        output += "<form method = 'GET' enctype='multipart/form-data' action=''>"
        output += "<input type = 'submit' name = 'back' value = 'Back'></form>"
        return output

def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print("Web server running on port {}".format(port))
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()


if __name__ == '__main__':
    main()