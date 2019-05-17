"""For running on uwsgi"""

from pemoi import app as application

if __name__ == '__main__':
	application.run()

