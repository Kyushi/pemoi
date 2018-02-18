#!/usr/bin/python
from flipflop import WSGIServer
from pemoi import app

if __name__ == '__main__':
    WSGIServer(app).run()
