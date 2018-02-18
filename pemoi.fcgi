#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from pemoi import app

class ApacheUberspaceRewriteFix():
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = ''
        return self.app(environ, start_response)

if __name__ == '__main__':
    WSGIServer(ApacheUberspaceRewriteFix(app)).run()