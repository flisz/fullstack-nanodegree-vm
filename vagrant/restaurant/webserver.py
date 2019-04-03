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
            print("GET: {}".format(self.path))
            self.send_output()
        except IOError:
            self.send_error(404, "File Not Found: {}".format(self.path))

    def do_POST(self):
        try:
            print("POST: {}".format(self.path))
            self.send_response(301)
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            print(ctype)
            print(pdict)
            if pdict.get('boundary') is not None:
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message') 
            self.send_output()
        except IOError:
            self.send_error(404, "File Not Found: {}".format(self.path))

    def restaurant_add(self):
        pass

    def do_PUT(self):
        try:
            print("DELETE: {}".format(self.path))
            self.send_response(301)
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            print(ctype)
            print(pdict)
            if pdict.get('boundary') is not None:
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message') 
            self.send_output()
        except IOError:
            self.send_error(404, "File Not Found: {}".format(self.path))

    def restaurant_edit(self):
        pass

    def do_DELETE(self):
        try:
            print("DELETE: {}".format(self.path))
            self.send_response(301)
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            print(ctype)
            print(pdict)
            if pdict.get('boundary') is not None:
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message') 
            self.send_output()
        except IOError:
            self.send_error(404, "File Not Found: {}".format(self.path))

    def restaurant_delete(self):
        pass

    def send_output(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        output = self.render_page()
        self.wfile.write(output.encode('utf-8'))
        
    def render_page(self):
        output = ""
        output += "<html><body>"
        if self.path == "/restaurants":
            output = self.render_restaurants(output)
        else:
            sp = self.path.split("/")
            print("path_list:\t{}".format(sp))
            if sp[1] == "restaurants":
                if len(sp) == 3:
                    if sp[2] == "new":
                        output = self.render_restaurant_new(output)
                elif len(sp) == 4:
                    path_id = sp[2]
                    if sp[3] == "edit":
                        output = self.render_restaurant_edit(output, path_id)
                    elif sp[3] == "delete":
                        output = self.render_restaurant_delete(output, path_id)
                elif len(sp) > 4:
                	output = self.render_restaurants(output)

        output += "</body></html>"
        return output

    def render_restaurants(self, output):
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
                output += "<form method = 'POST' enctype='multipart/form-data' action='restaurants/{}/edit'>".format(restaurant.id)
                output += "<input type = 'submit' value = 'Edit'></form>"
                output += "</td>"
                #delete button
                output +="<td>"
                output += "<form method = 'POST' enctype='multipart/form-data' action='restaurants/{}/delete'>".format(restaurant.id)
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
            output += "<form method = 'POST' enctype='multipart/form-data' action='submit'>".format(restaurant.id)
            output += "<input type = 'submit' value = 'Submit Edit'></form>"
            output += "<form method = 'POST' enctype='multipart/form-data' action='back'>".format(restaurant.id)
            output += "<input type = 'submit' value = 'Go Back'></form>"
        return output

    def render_restaurant_delete(self, output, path_id):
        stage = DBSessionMaker()
        print("path_id: {}, type:{}".format(path_id,type(path_id)))
        restaurants = stage.query(Restaurant).filter(Restaurant.id == path_id)
        for restaurant in restaurants:
            output += "<h4>Confirm Delete Restaurant: {}</h4>".format(restaurant.name)
            output += "<form method = 'POST' enctype='multipart/form-data' action='submit'>"
            output += "<input type = 'submit' value = 'Confirm Delete'></form>"
        return output

    def render_restaurant_new(self, output):
        stage = DBSessionMaker()
        restaurants = stage.query(Restaurant).filter(Restaurant.name == path_id)
        output += "<h4>New Restaurant:</h4>"
        output += "<form method = 'POST' enctype='multipart/form-data' action='restaurants/new'>".format(restaurant.id)
        output += "<input type = 'submit' value = 'Submit_new'></form>"
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