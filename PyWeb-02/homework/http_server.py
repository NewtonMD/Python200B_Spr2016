'''______________________________________________________
Mike Newton
newton33@uw.edu
Web Programming With Python 100
University of Washington, Spring 2016
Last Updated:  13 April 2016
Python Version 3.5.1
______________________________________________________'''

import socket
import sys
import os
import mimetypes as mt
import pathlib as pl

def response_ok(body, mimetype):
    """returns a basic HTTP response"""
    #check to see if we need to encode mimetype
    try:
        mimetype = mimetype.encode('utf8')
    except AttributeError:
        pass
    
    #check to see if we need to encode body
    try:
        body = body.encode('utf8')
    except AttributeError:
        pass
    
    
    resp = []
    resp.append(b"HTTP/1.1 200 OK")
    resp.append(b"Content-Type:" + mimetype)
    resp.append(b"")
    resp.append(body)
    return b"\r\n".join(resp)

def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp).encode('utf8')


def response_not_found():
    """returns a 404 Not Found response"""
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    return "\r\n".join(resp).encode('utf8')


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    return uri


def resolve_uri(uri):
    #set home directory
    home = 'webroot'
    #get path of URI
    pname = home + uri
    #get full path to file/dir
    fullpath = os.path.realpath(pname)
    
    #if URI is a directory, return a list of it's contents and a mimetype of text/plain
    #raise NameError if URI doesn't exist
    if os.path.isdir(fullpath):
        fnames = os.listdir(fullpath)
        content = '\n'.join(''.join(i) for i in fnames)
        mime_type = "text/plain"
    elif os.path.isfile(fullpath):
        f = open(fullpath, 'rb')
        content = f.read()
        f.close()
        mime_type = mt.guess_type(fullpath)[0]
    elif not os.path.exists(fullpath):
        response = response_not_found()
    
    """This method should return appropriate content and a mime type"""
    
    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')
                    if len(data) < 1024:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    try:
                        content, mime_type = resolve_uri(uri)
                    except NameError:
                        response = response_not_found()
                    else:
                        response = response_ok(content, mime_type)

                print('sending response', file=log_buffer)
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
