#!/usr/bin/env python
#
# Copyright 2015 DrYve, LLC
# Author: Nicholas Gillespie
# Email: nick@dryve.io
#
import webapp2
import os
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext import ndb
import hashlib
from protorpc.messages import Enum
from google.appengine.api import users

import logging # TODO remove 


# CONSTANTS

NEWS_LETTER_SUBSCRIPTIONS_DATASTORE = 'NewsLetterSubscriptions'
DRIVER_SIGNUP_DATASTORE = 'DriverSignup'
ADVERTISER_SIGNUP_DATASTORE = 'AdsSignup'

VERIFY_NEWSLETTER = 'newsletter'
VERIFY_DRIVER = 'driver'
VERIFY_ADVERTISER = 'advertiser'

# DATA MODELS

class NewsLetterSubscriptions(ndb.Model):
    email = ndb.StringProperty()
    verify_id = ndb.StringProperty()
    verified = ndb.BooleanProperty(default=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_verify_id(cls, key):
        return cls.query().filter(cls.verify_id==key).order(-cls.verify_id)
        
class DriverInfo(ndb.Model):
    name = ndb.StringProperty()
    phone = ndb.StringProperty()
    email = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    company = ndb.PickleProperty()
    segments = ndb.IntegerProperty()
    mornings = ndb.IntegerProperty()
    midday = ndb.IntegerProperty()
    afternoon = ndb.IntegerProperty()
    latenight = ndb.IntegerProperty()
    verify_id = ndb.StringProperty()
    verified = ndb.BooleanProperty(default=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_verify_id(cls, key):
        return cls.query().filter(cls.verify_id==key).order(-cls.verify_id)
        
class AdvertiserInfo(ndb.Model):
    name = ndb.StringProperty()
    company = ndb.StringProperty()
    phone = ndb.StringProperty()
    email = ndb.StringProperty()
    target_market = ndb.StringProperty()
    territories = ndb.StringProperty()
    other_info = ndb.StringProperty()
    verify_id = ndb.StringProperty()
    verified = ndb.BooleanProperty(default=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_verify_id(cls, key):
        return cls.query().filter(cls.verify_id==key).order(-cls.verify_id)
        
class AdCampaign(ndb.Model):
    name = ndb.StringProperty()
    details = ndb.StringProperty()
    link = ndb.StringProperty()
    clicks = ndb.IntegerProperty(default=0)
    start_date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def add_click(cls, key):
        item = cls.query().filter(cls.link==key).order(-cls.start_date).get()
        if item == None:
            return False
        item.clicks = item.clicks + 1
        item.put()
        return True
        
    @classmethod
    def name_exist(cls, key):
        item = cls.query().filter(cls.name==key).order(-cls.start_date).get()
        if item == None:
            return False
        else:
            return True
        
 # REQUEST HANDLERS 

class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        template_vaules = {
            'message_class': 'no_message',
            'message_text': ' ',
        }
        self.response.out.write(template.render(path, template_vaules))
        
class AdvertiserSignup(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/ad_signup.html')
        tempate_values = {
            'message_class': 'no_message',
            'message_text': ' ',
        }
        self.response.out.write(template.render(path, tempate_values))
        
    def post(self):
        template_vaules = {
            'message_class': 'good_message',
            'message_text': 'Please check your inbox for a verification email.',
        }
        error = False
        advertiser = AdvertiserInfo()
        #get variables from POST and validate
        if Validate(self.request.get('name'), ValidationTypes.String, True) is True:
            advertiser.name = self.request.get('name')
        else:
            error = True
        if Validate(self.request.get('company'), ValidationTypes.String, True) is True:
            advertiser.company = self.request.get('company')
        else:
            error = True
        if Validate(self.request.get('phone'), ValidationTypes.String, True) is True:
            advertiser.phone = self.request.get('phone')
        else:
            error = True
        if Validate(self.request.get('email'), ValidationTypes.Email, True) is True:
            advertiser.email = self.request.get('email')
        else:
            error = True
        advertiser.target_market = self.request.get('target_market')
        advertiser.territories = self.request.get('territories')
        advertiser.other_info = self.request.get('other_info')
            
        #Check to see if error was found in validation of data
        if error is True:
            template_vaules['message_class'] = 'bad_message'
            template_vaules['message_text'] = "Make sure name, email, phone, and company fields are filled out"
        else:
            #data good = save and email advertiser
            advertiser.verify_id = hashlib.md5(advertiser.email).hexdigest()
            advertiser.put()
            #creat and send the email
            confirmation_url = 'http://dryve-web.appspot.com/verify/%s/' %VERIFY_ADVERTISER + advertiser.verify_id
            sender_address = "No-Reply <no-reply@dryve.io>"
            subject = "Confirm your email"
            body = """
Thank you for signing up for the drYve program! Please confirm your email address by
clicking on the link below:

%s
""" % confirmation_url
            mail.send_mail(sender_address, advertiser.email, subject, body)
            
        #send results to user
        path = os.path.join(os.path.dirname(__file__), 'templates/ad_signup.html')
        self.response.out.write(template.render(path, template_vaules))
        
        
class DriverSignup(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/signup.html')
        tempate_values = {
            'message_class': 'no_message',
            'message_text': ' ',
        }
        self.response.out.write(template.render(path, tempate_values))
        
    def post(self):
        template_vaules = {
            'message_class': 'good_message',
            'message_text': 'Please check your inbox for a verification email.',
        }
        error = False
        driver = DriverInfo()
        #get variables from POST and validate
        if Validate(self.request.get('name'), ValidationTypes.String, True) is True:
            driver.name = self.request.get('name')
        else:
            error = True
        if Validate(self.request.get('phone'), ValidationTypes.String, True) is True:
            driver.phone = self.request.get('phone')
        else:
            error = True
        if Validate(self.request.get('email'), ValidationTypes.Email, True) is True:
            driver.email = self.request.get('email')
        else:
            error = True
        if Validate(self.request.get('city'), ValidationTypes.String, True) is True:
            driver.city = self.request.get('city')
        else:
            error = True
        if Validate(self.request.get('state'), ValidationTypes.String, True) is True:
            driver.state = self.request.get('state')
        else:
            error = True
        if Validate(self.request.get('segments'), ValidationTypes.Integer, True) is True:
            driver.segments = int(self.request.get('segments'))
        else:
            error = True
            
        if Validate(self.request.POST.getall('company'), ValidationTypes.Array, True) is True:
            driver.company = self.request.POST.getall('company')
        else:
            error = True
            
        driver.mornings = int(self.request.get('mornings'))
        driver.midday = int(self.request.get('midday'))
        driver.afternoon = int(self.request.get('afternoon'))
        driver.latenight = int(self.request.get('latenight'))
        
        #Check to see if error was found in validation of data
        if error is True:
            template_vaules['message_class'] = 'bad_message'
            template_vaules['message_text'] = "Make sure all fields are filled out"
        else:
            #data good = save and email driver
            driver.verify_id = hashlib.md5(driver.email).hexdigest()
            driver.put()
            #creat and send the email
            confirmation_url = 'http://dryve-web.appspot.com/verify/%s/' %VERIFY_DRIVER + driver.verify_id
            sender_address = "No-Reply <no-reply@dryve.io>"
            subject = "Confirm your email"
            body = """
Thank you for signing up for the drYve program! Please confirm your email address by
clicking on the link below:

%s
""" % confirmation_url
            mail.send_mail(sender_address, driver.email, subject, body)
            
        #send results to user
        path = os.path.join(os.path.dirname(__file__), 'templates/signup.html')
        self.response.out.write(template.render(path, template_vaules))

class NewsLetter(webapp2.RequestHandler):
    def post(self):
        template_vaules = {
            'message_class': 'good_message',
            'message_text': 'Please check your inbox for a verification email.',
        }
        #gets veriables for database
        newsletter_email = self.request.get('newsletter_email')
        #verify email
        if not mail.is_email_valid(newsletter_email):
            # prompt user to neter a valid address 
            template_vaules['message_class'] = 'bad_message'
            template_vaules['message_text'] = "somethings wrong with the email you entered, please check and try again."
        else:
            verify_id = hashlib.md5(newsletter_email).hexdigest()
            #creates and saves database entry
            subscriber = NewsLetterSubscriptions()
            subscriber.email = newsletter_email
            subscriber.verify_id = verify_id
            subscriber.put()
            #create and send verification email
            confirmation_url = 'http://dryve-web.appspot.com/verify/%s/' %VERIFY_NEWSLETTER + verify_id
            sender_address = "No-Reply <no-reply@dryve.io>"
            subject = "Confirm your subscription"
            body = """
Thank you for signing up for the drYve newsletter! Please confirm your email address by
clicking on the link below:

%s
""" % confirmation_url
            mail.send_mail(sender_address, newsletter_email, subject, body)
            
            logging.info(confirmation_url)
            
        #let user know about email
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_vaules))
  
class AdHandler(webapp2.RequestHandler):
    def get(self, campaign_link):
        #add click to campaign
        AdCampaign.add_click(campaign_link)
        #route user to homescreen
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        template_vaules = {
            'message_class': 'no_message',
            'message_text': ' ',
        }
        self.response.out.write(template.render(path, template_vaules))

class VerifyAccount(webapp2.RequestHandler):
    def get(self, verify_type, verify_id):
        #get datastore object based on type
        if verify_type == VERIFY_NEWSLETTER:
            data = NewsLetterSubscriptions.query_verify_id(verify_id).get()
        elif verify_type == VERIFY_DRIVER:
            data = DriverInfo.query_verify_id(verify_id).get()
        elif verify_type == VERIFY_ADVERTISER:
            data = AdvertiserInfo.query_verify_id(verify_id).get()
        else:
            self.response.out.write("Sorry not sure were you are trying to go. If you got here from a link please let us know at contact@dryve.io")
            return
        #Update key in datastore based on id
        data.verified = True
        data.put()
        #inform user of results
        self.response.out.write("Thanks %s, your email has been verified!" % data.email)

class AdminRedirect(webapp2.RequestHandler):
    def get(self):
        self.redirect(self.request.url+'/')

#Utility Functions
        
class ValidationTypes(Enum):
    String = 1
    Integer = 2
    Email = 3
    Array = 4
        
def Validate(data, typ, empty=False):
    if typ is ValidationTypes.String:
        if isinstance(data, unicode) == False:
            return False
        if empty is True:
            if data is  None or len(data) == 0:
                return False
    elif typ is ValidationTypes.Integer:
        logging.info(data)
        if len(data) is 0:
            return False
        if isinstance(int(data), int) == False:
            return False
        if empty is True:
            if data is None:
                return False
    elif typ is ValidationTypes.Email:
        if mail.is_email_valid(data) == False:
            return False
        if empty is True:
            if data is None or len(data) == 0:
                return False
    elif typ is ValidationTypes.Array:
        if len(data) == 0:
            return False
    
    return True
    
                 
# ROOT

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signup/advertiser', AdvertiserSignup),
    ('/signup/driver', DriverSignup),
    ('/signup', DriverSignup),
    ('/newsletter', NewsLetter),
    (r'/verify/(\w+)/(\w+)', VerifyAccount), #/verify/<datastore object>/<verify id>
    (r'/ad/(\w+)', AdHandler), #/ad/<campaign link>
    ('/admin', AdminRedirect),
], debug=False)
