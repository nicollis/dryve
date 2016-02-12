#!/usr/bin/env python
#
# Copyright 2015 DrYve, LLC
# Author: Nicholas Gillespie
# Email: nick@dryve.io
#
import webapp2
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
import hashlib
from google.appengine.api import users
#import Data Object used in main.py
from main import AdCampaign, DriverInfo, AdvertiserInfo, NewsLetterSubscriptions, Validate, ValidationTypes

import logging

USER_INFO_SCREEN_DRIVERS = 'drivers'
USER_INFO_SCREEN_ADVERTISERS = 'advertisers'
USER_INFO_SCREEN_NEWSLETTER = 'newsletter'

class AdCampaignHandler(webapp2.RequestHandler):

    def get(self):
        template_vaules = {
            'message_class': 'no_message',
            'message_text': ' ',
            'logout_btn_class' : 'show',
            'logout_url' :  users.create_logout_url('/'),
            'campaigns' : (AdCampaign().query().order(-AdCampaign.start_date)).iter(),
            'admin' : True,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/ad_campaign.html')
        self.response.out.write(template.render(path, template_vaules))
        
    def post(self):
        t_template_vaules = {
            'message_class': 'no_message',
            'message_text': ' ',
            'logout_btn_class' : 'show',
            'logout_url' :  users.create_logout_url('/'),
            'admin' : True,
        }
        error = False
        campaign = AdCampaign()
        #get variables from POST and validate if needed
        if Validate(self.request.get('name'), ValidationTypes.String, True) is True:
            campaign.name = self.request.get('name')
        else:
            error = True
            t_template_vaules['message_text'] = 'Name required to start a campaign'
        campaign.details = self.request.get('details')
        #check if name is already in use
        if campaign.name_exist(campaign.name) is True:
            error = True
            t_template_vaules['message_text'] = 'Name: %s, is already in use.' %campaign.name
        #check for errors
        if error is False:
            #create link
            campaign.link = hashlib.md5(campaign.name).hexdigest()
            campaign.put()
            t_template_vaules['ad_campaign_url'] = "campaign link is: dryve.io/ad/%s" %campaign.link
        else:
            t_template_vaules['message_class'] = 'bad_message'
        #save and returns results
        t_template_vaules['campaigns'] = (AdCampaign().query().order(-AdCampaign.start_date)).iter()
        path = os.path.join(os.path.dirname(__file__), 'templates/ad_campaign.html')
        self.response.out.write(template.render(path, t_template_vaules))
        
class UserInfoHandler(webapp2.RequestHandler):#todo start working here
    def get(self, requested_data):
        t_template_vaules = {
            'message_class': 'no_message',
            'message_text': ' ',
            'logout_btn_class' : 'show',
            'logout_url' :  users.create_logout_url('/'),
            'admin' : True,
        }
        if requested_data == USER_INFO_SCREEN_DRIVERS:
            t_template_vaules['driver'] = True
            t_template_vaules['title'] = "Driver Signup"
            t_template_vaules['data'] = (DriverInfo.query().filter(DriverInfo.verified==True).order(-DriverInfo.date)).iter()
        elif requested_data == USER_INFO_SCREEN_ADVERTISERS:
            t_template_vaules['advertiser'] = True
            t_template_vaules['title'] = "Advertiser Signup"
            t_template_vaules['data'] = (AdvertiserInfo.query().filter(AdvertiserInfo.verified==True).order(-AdvertiserInfo.date)).iter()
        elif requested_data == USER_INFO_SCREEN_NEWSLETTER:
            t_template_vaules['newsletter'] = True
            t_template_vaules['title'] = "Newsletter Signup"
            t_template_vaules['data'] = (NewsLetterSubscriptions.query().filter(NewsLetterSubscriptions.verified==True).order(-NewsLetterSubscriptions.date)).iter()
        
        
        path = os.path.join(os.path.dirname(__file__), 'templates/user_info.html')
        self.response.out.write(template.render(path, t_template_vaules))
        
class AdminHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect(self.request.url+'campaigns')


app = webapp2.WSGIApplication([
    ('/admin/', AdminHandler),
    ('/admin/campaigns', AdCampaignHandler),
    (r'/admin/user_info/(\w+)', UserInfoHandler),
], debug=True)