## COS 460/540 - Computer Networks
# Project 2: HTTP Server

# William Lago

This project is written in Python on Linux.

## How to compile

No compilation required; see below.

## How to run

* Ensure Python is installed and up-to-date.
* Navigate to the project directory in Terminal.
* Enter "http_server.py \<port\> www" to launch the server on the given localhost port.
* Connect to localhost:\<port\> in any web browser to view the sample index.html.
* "telnet localhost \<port\>" can also be used to directly connect to the server and send it keyboard input, useful for testing error responses and concurrent connections.

## My experience with this project

This was certainly more involved than Project 1's command server. I started out with a similar simple echo server and then expanded it to parse input and recognize HTTP request lines, splitting the first line of any incoming message into three space-separated parts (request type, path, and version) if possible and throwing an error (400 Bad Request) if not. Then, anything that didn't start with a request type of GET was also thrown out with an error (501 Not Implemented). If a valid GET request was detected, a 200 OK response was sent and the requested file path was opened and read.

It was around this point that I became aware of the possibility of malicious file paths abusing /.. to escape the root directory, so I added an extra function (safe_join) to normalize paths and ensure that they can't leave the document root. For actually serving files to clients, the send_response function was designed to be modular, accepting any type of data in the form of binary as the body content along with arguments for the client socket, response code, and mime type; this same function is used for sending error responses (in which the body content is just the error code and description) along with OK responses (in which the body content is the requested file from the document root). To determine which MIME header to return, I used mimetype.guess_type to automatically detect the MIME type of a requested file.

Setting up threading was one of the last things I did, and it was actually easier than I expected; the Python threading library handles most of the low-level work, so all I had to do was replace a direct call to my handle_request function with a call to create a new thread with handle_request as its target. I also added some logging output that displays client connections/disconnects, as well as the total number of active threads whenever a new client connects.
