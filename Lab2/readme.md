# TASK 1
# Description
Web server built in python that handles http requests. 
The server supports GET and HEAD requests.

# How to use
Navigate to the Lab2Task1 folder

`cd Lab2Task1`

Run the webserver

`python webserver.py`

Open a web browser

http://127.0.0.1:10200/HelloWorld.html
http://127.0.0.1:10200/data/foo.html

Enter a file which does not exist and 404 not found will be returned

http://127.0.0.1:10200/not/existingfile.html

Alternatively open Postman and submit the following requests.

GET http://127.0.0.1:10200/HelloWorld.html 

HEAD http://127.0.0.1:10200/data/foo.html

GET http://127.0.0.1:10200/not/existingfile.html

To close the webserver

`ctrl + c`


# TASK 2
# Description
Module to send and receive DNS queries and responses

# Setup
Ensure bitstruct is installed

# Executiom
In one terminal run server.py, in the other run client.py.
Ensure they are in the same directory, along with DNSMessage.py

`python3 server.py`

`python3 client.py`

Server.py must be started first. You can then enter valid domain names
in the client.py terminal
