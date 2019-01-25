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
    
    def handle(self):
        #TODO show files
        self.request.settimeout(1)

        self.data = self.request.recv(1024).strip().decode("utf-8")
        http_command = self.data.split(" ")[0]
        path = self.data.split(" ")[1]

        #if path == "/../../../../../../../../../../../../etc/group":
        #    print("testing")

        print("Got a request of: %s\n" % self.data)

        response = self.get_response(path, http_command)

        self.request.sendall(bytearray(response, 'utf-8'))

    def get_response(self, path, http_command):
        if http_command != "GET":
            response = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\ncharset=UTF-8\r\n\r\n"
        elif path == "/":
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\ncharset=UTF-8\r\n\r\n"
            html = open("./www/index.html").read()
            html = self.add_file_names("./www", html)
            response += html
        elif path == "/deep/":
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\ncharset=UTF-8\r\n\r\n"
            html = open("./www/deep/index.html").read()
            html = self.add_file_names("./www/deep", html)
            response += html
        elif path == "/deep":
            response = "HTTP/1.1 301 Moved Permanently\r\nContent-Type: text/plain\r\ncharset=UTF-8\r\n" \
                       "Connection: keep-alive\r\nLocation: http://localhost:8080/deep/\r\n\r\n"
            html = "301 Moved Permanently"
            response += html
        else:
            file_contents = self.get_file_contents(path)
            if file_contents is not None:
                file_type = path.split(".")[-1]
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/"+file_type+"\r\ncharset=UTF-8\r\n\r\n"
                response += file_contents
            else:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\ncharset=UTF-8\r\n\r\n"
                html = "404 Not Found"
                response += html
        return response

    @staticmethod
    def add_file_names(folder_path, html):
        split_html = html.split("</ul>")
        file_names = os.listdir(folder_path)

        for file_name in file_names:
            if os.path.isdir(folder_path + "/" + file_name):
                continue
            split_html[0] += "<li><a href="+file_name+">"+file_name+"</a></li>\n"
        return "".join(split_html)

    @staticmethod
    def get_file_contents(path):
        path_sections = path.split("/")[:-1]
        for path_section in path_sections:
            if path_section == "..":
                return None

        folder_path = "./www"+path

        try:
            return open(folder_path, "r").read()
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
