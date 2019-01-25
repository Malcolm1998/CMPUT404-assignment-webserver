#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    # handles the request
    def handle(self):
        # noinspection PyAttributeOutsideInit
        self.data = self.request.recv(1024).strip().decode("utf-8")

        # print("Got a request of: %s\n" % self.data)
        if self.data == "":
            return

        http_command = self.data.split(" ")[0]
        path = self.data.split(" ")[1]

        response = self.get_response(path, http_command)

        self.request.sendall(bytearray(response, 'utf-8'))

    # returns the appropriate response given the path and http command
    def get_response(self, path, http_command):
        local_path = "./www" + path
        if http_command != "GET":
            response = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\ncharset=UTF-8\r\n\r\n"
            html = "405 Method Not Allowed"
            response += html
        elif os.path.isdir(local_path):
            if local_path[-1] != "/":
                response = "HTTP/1.1 301 Moved Permanently\r\nContent-Type: text/html\r\ncharset=UTF-8\r\n" \
                           "Location:" + path + "/\r\n\r\n"
                html = "301 Moved Permanently"
                response += html
            else:
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\ncharset=UTF-8\r\n\r\n"
                html = open(local_path+"/index.html").read()
                html = self.add_directory_names(local_path, path, html)
                response += html
        else:
            file_contents = self.get_file_contents(local_path)
            if file_contents is not None:
                file_type = path.split(".")[-1]
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/"+file_type+"\r\ncharset=UTF-8\r\n\r\n"
                response += file_contents
            else:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\ncharset=UTF-8\r\n\r\n"
                html = "404 Not Found"
                response += html
        return response

    # adds the list of folders, html files and css files to the main html as clickable links
    @staticmethod
    def add_directory_names(local_path, path, html):
        split_html = html.split("</ul>")
        file_names = os.listdir(local_path)

        for file_name in file_names:
            if os.path.isdir(local_path+"/"+file_name):
                split_html[0] += "<li><a href="+path+file_name+"/>"+file_name+"</a></li>\n"

        for file_name in file_names:
            if os.path.isfile(local_path+"/"+file_name):
                split_html[0] += "<li><a href="+path+file_name+">"+file_name+"</a></li>\n"

        return "".join(split_html)

    # This loads a files' contents, if it exits, or it returns None
    @staticmethod
    def get_file_contents(local_path):
        path_sections = local_path.split("/")
        for path_section in path_sections:
            if path_section == "..":
                return None

        try:
            return open(local_path, "r").read()
        except FileNotFoundError:
            return None
        except NotADirectoryError:
            return None


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    try:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
