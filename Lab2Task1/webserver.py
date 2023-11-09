import socket
from datetime import datetime
import os
import time

HOME_IP_ADDRESS = "127.0.0.1"
PORT = 10200 # Arbitrary unused port

# Scope only supports 2 responses
STATUS_200 = "HTTP/1.1 200 OK"
STATUS_404 = "HTTP/1.1 404 Not Found"

def CreateResponseHeader(connection="keep-alive", date="", server="Webserver", last_modified="", content_length="0", content_type="text/html; charset=UTF-8\r\n"):
    date = time.asctime(time.localtime())
    return f"""
Connection: {connection}
Date: {date}
Server: {server}
Last-Modified: {last_modified}
Accept-Ranges: bytes
Content-Length: {content_length}
Content-Type: {content_type}
"""

# Process HTTP request and put headers in data structure
def HTTPHeaders(request):
    headers = {}
    for i, line in enumerate(request.splitlines()):
        if i == 0: # status line
            headers["METHOD"] = line.split(' ')[0]
            headers["PATH"] = line.split(' ')[1]
            headers["Version"] = line.split(' ')[2]
        else:
            headers[line.split(":")[0]] = line.split(':')[1]
    return headers

if __name__ == "__main__":
    # create and configure websocket as ipv4, tcp, resuable, and ip:port
    webserver = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    webserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    webserver.bind((HOME_IP_ADDRESS, PORT))

    while True:
        webserver.listen(0) # inifinite buffer
        client_socket, client_address = webserver.accept() # wait for incoming connection

        request = client_socket.recv(1024).decode("utf-8").strip() # decode bytes to string
        headers = HTTPHeaders(request=request) # put headers into dict

        # check if file is found
        fileName = os.getcwd() + headers["PATH"]
        filePresent = os.path.isfile(fileName)

        if filePresent: # if present, grab contents and create headers for response
            fileSize = os.stat(fileName).st_size
            last_modified = time.ctime(os.path.getmtime(fileName))
            response = STATUS_200 + CreateResponseHeader(content_length=str(fileSize),last_modified=last_modified)

            if headers["METHOD"] == "GET":
                with open(os.getcwd() + headers["PATH"], "r") as file_content:
                    data = file_content.read()
                response += data # add file content to response
        else:
            lengthBytes = len("404 Not Found".encode('utf-8'))
            response = STATUS_404 + CreateResponseHeader(content_length=lengthBytes) 
            if headers["METHOD"] == "GET":
                response += "404 Not Found"
        
        client_socket.send(response.encode("utf-8"))
        client_socket.close()
        # webserver.close()
