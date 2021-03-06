
'''
careercentral.herokuapp.com/API=123,role=python, location=New York
'''
from django.http import HttpResponse, StreamingHttpResponse
import json 
from .scrape.indeed_refactor import Indeed
from .scrape import multiprocess_simply, multithread_simply, async_monster, builder
from.scrape.async_monster import run
from django.contrib.auth.models import User
import secrets
from .models import getkey, insert_key, get_allkeys

'''
class variables handling weird in heroku environ. Due to multiple processes
handling http requests. solution: save the api key in the db in a email:token table with email as pk

'''

class Generate_Token():
    active_keys={}
    def __init__(self, email): 
        self.key=None
        self.email=email
        self.errors={}
    
    def activate_key(self):
        token=secrets.token_urlsafe(10)
        self.addtoactive(self.email, token)
        insert_key(self.email, token)
        return token
    
    def get_userkey(self):
        return getkey(self.email)
    @classmethod
    def addtoactive(cls, email, token):
        cls.active_keys[email]=token
        print('all keys ', cls.active_keys)
    @classmethod
    def getallkeys(cls):
        return cls.active_keys
    
    def error_handler(self):
        self.errors={"1" : "error"}
        return HttpResponse(self.errors)

class Api_Response():
    def response(self, token, role , location, engine):
        active_keys=Generate_Token('api').getallkeys() 
        self.errors={'error':'errors'}
        engines=['Indeed', 'Monster', 'Simply', 'Builder']
        if (any(token in i for i in get_allkeys())) :
            if engine=='Indeed':
                ret=Indeed().getrole(role, location)
            elif engine=='Simply':
                ret=multiprocess_simply.getrole_simply(role,location)
            elif engine=='Builder':
                ret=builder.getrole_career(role,location) 
            elif engine=='Monster':
                ret=run(async_monster.getrole_monster(role, location))
            else:
                return HttpResponse( json.dumps(
                    {'error':  '{} {}'.format('Please use a valid engine name ', engines)}
                    ))
            return HttpResponse (
                json.dumps({ 
                    'Role': role, 
                    'Location': location, 
                    'Jobs': ret
                    }  , indent=4))

        else:
            return HttpResponse( json.dumps(
                    {'error': '{} {}'.format( token , ' is an invalid token ')}
                    ))

    def error_handler(self):
        self.errors={"1" : "error"}
        return HttpResponse(self.errors)