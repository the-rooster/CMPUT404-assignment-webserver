#  coding: utf-8 
import socketserver
from urllib.parse import urlparse
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

BASE_DIRECTORY = "./www/"


class MyWebServer(socketserver.BaseRequestHandler):


    valid_extensions = {"html","css"}
    
    def get(self,path):
        
        path = os.path.normpath(path)

        print("NORMALIZED PATH!: ",path)

        total = BASE_DIRECTORY + path

        file = path.split("/")[-1]

        #if a directory is requested, serve the index.html within if it exists
        if path[-1] == "/":
            path += "index.html" 
            total = BASE_DIRECTORY + path
            file = path.split("/")[-1]

        #if there is no file extension, the user has requested a directory incorrectly. redirect them
        if "." not in file:
            fixed_path = path + "/"
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently \nLocation: {fixed_path}\nConnection: Closed",'utf-8'))
            return

        #get file extension
        file_ext = file.split(".")[-1]

        #make sure file_ext is valid and derive mime_type. this webserver only hosts html and css
        if not file_ext in self.valid_extensions:
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found ",'utf-8'))
            return

        mime_type = f"text/{file_ext}"

        print("MIME TYPE: " + mime_type)
        if not os.path.exists(total):
            print("FILE NOT FOUND!")
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found ",'utf-8'))
            return
        
        contents = None

        with open(total,"r") as f:
            contents = f.read()

        self.request.sendall(bytearray(f'HTTP/1.1 200 OK \nLocation: {path}\nContent-Type: {mime_type}\nConnection: Closed\n\n{contents}\n','utf-8'))   
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        #parse HTTP request
        req_lines = self.data.decode('utf-8').split("\n")
        req_info = req_lines[0].split(" ")

        if len(req_info) < 2:
            return
            
        req_method = req_info[0]
        req_path = req_info[1]
        
        print(req_method,req_path)
        if req_method.lower() != "get":
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed ",'utf-8'))
            return
        
        parsed_path = urlparse(req_path)

        print(parsed_path)
        self.get(parsed_path.path)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
