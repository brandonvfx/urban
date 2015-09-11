#!/usr/bin/env python

import os
import re
import sys
import json
import urllib2
import cgi

from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask import escape

import requests

import generate
import hall_of_fame

abort = False

app = Flask(__name__)

def find_image(phrase, animated=False, unsafe=False):
    attempts = 0

    qs = {
        "v": 1.0,
        "q": phrase,
        "imgsz": "large",
        "userip": request.remote_addr,
    }
    if not unsafe:
        qs["safe"] =  "active",

    ext_filters = ['.jpg', '.png', '.gif']
    #ext_filters = ['.jpg']
    #Kind of working :-/
    if animated:
        qs["as_filetype"] = "gif"
        ext_filters = ['.gif']

    resp = requests.get("https://ajax.googleapis.com/ajax/services/search/images", params=qs)
    if resp.status_code == 200:
        results = resp.json()
        for imgdict in results['responseData']['results']:
            img_url = imgdict['url']
            _, ext = os.path.splitext(img_url)
            if ext.lower() in ext_filters:
                return img_url

    return ""

def space_to_plus(mystr):
    return re.sub(" ","+", mystr)    

def colon_to_pct(mystr):
    return re.sub(":","%3A", mystr)    

@app.route('/')
def index():

    random = False
    unsafe = False
    animated = False 
    base = "http://%s"%request.environ['HTTP_HOST']
    curr = base
    animchecked = ""
    unsfchecked = ""
    randchecked = ""
    if request.args.get('a') is not None:
        animated = True
        animchecked = "checked"
    if request.args.get('u') is not None:
        unsafe = True
        unsfchecked = "checked"
    if request.args.get('r') is not None:
        random = True
        randchecked = "checked"

    if request.args.get('adj') and request.args.get('noun') and request.args.get('imgurl'):
        adj = escape(request.args.get('adj'))
        noun = escape(request.args.get('noun'))
        imgurl = escape(request.args.get('imgurl'))
    else:
        adj,alt_adj,noun,alt_noun = generate.random_phrase_2()
        imgroot = '%s %s'%(alt_adj,noun)
        if random:
            imgroot = '%s %s'%(alt_adj,alt_noun)
        imgurl = find_image(imgroot, animated, unsafe) 

    root = '%s %s'%(adj,noun)
    thisview = "http://%s?adj=%s&noun=%s&imgurl=%s"%(request.environ['HTTP_HOST'], 
        space_to_plus(adj),space_to_plus(noun), imgurl)

    quote=urllib2.quote(colon_to_pct(thisview))

    if request.args.get('hof') is not None:
        table = hall_of_fame.build_table()
        return render_template('halloffame.html.tpl', table=table )
    else:    
        return render_template('index.html.tpl', text=root, img=imgurl, 
            permalink=thisview, current_url=curr, baseurl=base, quotelink=quote,
            animchecked=animchecked, unsfchecked=unsfchecked, randchecked=randchecked)


if __name__ == '__main__':
    app.run(debug=True)
