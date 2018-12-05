import cherrypy
import os.path

from controller.proxy_controller import Proxy

configfile = os.path.join(os.path.dirname(__file__), 'config/server.conf')
cherrypy.quickstart(Proxy(), config=configfile)
