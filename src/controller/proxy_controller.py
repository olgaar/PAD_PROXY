# @cherrypy.expose
# def api(self, *args, **kwargs):
#     print("HEADERS2")
#     print(cherrypy.request.headers)
#     print("PARAMS2")
#     print(cherrypy.request.params)
#     cherrypy.response.headers = cherrypy.request.headers
#     if cherrypy.request.method == "POST":
#         cherrypy.response.headers['Content-Type'] = "application/json"
#         dictionary = {"name": "DachKib", "s_s": "dead"}
#         return json.dumps(dictionary).encode()
#     return "Well done"

# def handle_put(self):
#     requested_url = urlp.urlparse(cherrypy.url())
#     print("url")
#     print(requested_url)
#     url = "http://" + \
#           self.list_of_addresses[
#               random.randint(
#                   0, len(self.list_of_addresses) - 1)] + requested_url.path
#     resp = requests.get(url, cherrypy.request.params, headers=cherrypy.request.headers)
#     return resp
#
# def handle_patch(self):
#     requested_url = urlp.urlparse(cherrypy.url())
#     print("url")
#     print(requested_url)
#     url = "http://" + \
#           self.list_of_addresses[
#               random.randint(
#                   0, len(self.list_of_addresses) - 1)] + ""
#     resp = requests.get(url, cherrypy.request.params)
#     return resp
import urllib.parse as urlp
import requests
import cherrypy
import random
import json
import hashlib


class Proxy(object):
    def __init__(self):
        self.cache = {}
        data = json.load(open('config/nodes_config.json'))
        self.list_of_addresses = []
        for address in data['nodes']:
            self.list_of_addresses.append(address['address'])
        print(self.list_of_addresses)

    @cherrypy.expose
    def default(self, *args, **kwargs):
        # headers and query params
        headers = cherrypy.request.headers

        if cherrypy.request.method == "GET":
            return self.handle_get(headers)
        if cherrypy.request.method == "POST":
            return self.handle_post(headers)

        # if cherrypy.request.method == "PATCH":
        #     return self.handle_patch()
        # if cherrypy.request.method == "PUT":
        #     return self.handle_put()
        return "This method is not implemented"

    @cherrypy.expose
    def index(self, *args, **kwargs):
        print("headers")
        print(cherrypy.request.headers)
        return "It doesn't work!"

    def handle_get(self, headers):
        requested_url = urlp.urlparse(cherrypy.url())
        path = str(requested_url.path)
        accept_types = headers["Accept"].split(";")
        for types in accept_types:
            print("Types: " + str(types))
            params_str1 = requested_url.path
            params_str = requested_url.path + "; charset=utf-8"
            m = hashlib.md5()
            m.update(params_str.encode())
            params_str = m.hexdigest()
            m = hashlib.md5()
            m.update(params_str1.encode())
            params_str1 = m.hexdigest()
            print("MD5-1: " + str(params_str))
            if params_str in self.cache:
                print("Cache response")
                #cherrypy.response.headers["Content-Type"] = types
                return self.cache[params_str].encode()
            if params_str1 in self.cache:
                print("Cache response")
                #cherrypy.response.headers["Content-Type"] = types
                return self.cache[params_str].encode()
        rand = random.randint(0, len(self.list_of_addresses) - 1)
        print("random: " + str(rand))
        url = "http://" + self.list_of_addresses[rand] + requested_url.path
        print("url " + str(url))
        resp = requests.get(url, headers=headers)
        for types in accept_types:
            if resp.headers["Content-Type"] == types or resp.headers["Content-Type"] == (types + "; charset=utf-8"):
                print("Adding to cache")
                print(resp.content)
                params_str = path
                m = hashlib.md5()
                m.update(params_str.encode())
                params_str = m.hexdigest()
                print("MD5-2: ")
                print(params_str)
                self.cache[params_str] = resp.content.decode()
                print("Cache")
                print(self.cache)
        for key, value in resp.headers.items():
           cherrypy.response.headers[key] = value
        print(resp.headers)
        return resp

    def handle_post(self, headers):
        requested_url = urlp.urlparse(cherrypy.url())
        self.cache.clear()
        rand = random.randint(0, len(self.list_of_addresses) - 1)
        print("random: " + str(rand))
        url = "http://" + self.list_of_addresses[rand] + requested_url.path
        # url = "http://192.168.1.25:8080/api"
        resp = requests.post(url, cherrypy.request.body.read().decode(), headers=headers)
        for key, value in resp.headers.items():
            cherrypy.response.headers[key] = value
        return resp
