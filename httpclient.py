#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Jawad Hossain, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def getResponseBody(self, data):
        data = data.split("\n")

        headerEndIndex = data.index('\r')
        slice = data[headerEndIndex + 1 : len(data)]
        return "\n".join(slice)

    '''
        url encode args
    '''
    def prepareArgsForBody(self, args):
        body = ""
        counter = 0

        for key, value in args.items():
            body += f'{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(value)}'
            counter +=1
            
            # If there is more key-value pairs add separator            
            if (counter != len(args)):
                body += '&'
        
        return body


    def GET(self, url, args=None):

        parseResult = urllib.parse.urlparse(url)
        port = parseResult.port if parseResult.port else 80
        path = parseResult.path if parseResult.path else "/"
        query = f"?{parseResult.query}" if parseResult.query else ""
        path += query

        if args:
            encodedArgs = self.prepareArgsForBody(args)

            # if query params don't exist then add ?
            if (not query):
                path += '?'

            path += f'?{encodedArgs}'

        self.connect(parseResult.hostname, port)    
        requestData = f"GET {path} HTTP/1.1\r\nHost: {parseResult.hostname}\r\nConnection: close\r\nAccept:text/html\r\n\r\n"
        self.sendall(requestData)

        response = self.recvall(self.socket)
        code = int(response.split(' ')[1])
        body = self.getResponseBody(response)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        parseResult = urllib.parse.urlparse(url)
        port = parseResult.port if parseResult.port else 80
        path = parseResult.path if parseResult.path else "/"
        query = f"?{parseResult.query}" if parseResult.query else ""

        path += query

        # get args for body
        requestBody = ''
        if (args):
            requestBody = self.prepareArgsForBody(args)

        self.connect(parseResult.hostname, port)    
        requestData = f"POST {path} HTTP/1.1\r\nHost: {parseResult.hostname}\r\nContent-type: application/x-www-form-urlencoded\r\nContent-length: {len(requestBody)}\r\n\r\n{requestBody}\r\n"
        self.sendall(requestData)

        response = self.recvall(self.socket)
        code = int(response.split(' ')[1])
        body = self.getResponseBody(response)

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        HTTPresponse = client.command( sys.argv[2], sys.argv[1] )
        print(HTTPresponse.code, "\n", HTTPresponse.body)
    else:
        HTTPresponse = client.command( sys.argv[1] )
        print(HTTPresponse.code, "\n", HTTPresponse.body)

