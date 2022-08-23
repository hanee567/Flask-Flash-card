Python modules needed to be installed:
json
os
flask
datetime
flask_sqlalchemy
flask_restful
werkzeug

Imports required:
import json
import os
from flask import Flask,render_template,request,redirect,make_response
import datetime as dt
from flask_sqlalchemy import SQLAlchemy #Database managing
from flask_restful import Resource,Api
from werkzeug.exceptions import HTTPException

Initializing the application:
app=Flask(__name__)
setting config of the app.config
db=SQLAlchemy(app)
api=Api(app)

Setting all the endpoint view functions.

Running the application:
app.run(host,debug,port)

