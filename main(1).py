import json #Json (For APIs stuff)
import os #Managing modules directories etc
from flask import Flask
from flask_restful import Api
import logging
from flask_migrate import Migrate
logging.basicConfig(filename='debug.log',level=logging.DEBUG,format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s %(message)s')
app=Flask(__name__)

current_dir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #To suppress warning RSAWarning
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(current_dir,'database.sqlite3')


from application.database import db
db.init_app(app)
migrate=Migrate(app,db)
api=Api(app)
app.app_context().push()
app.config['SECRET_KEY']='Cannot guess'

from application.models import *  
from application.controllers import *

#APIs
from application.API import *  

api.add_resource(UserAPI,'/<string:username>/')
api.add_resource(UserDeckAPI,'/user/<int:user_id>/<int:deck_id>/','/user/<int:user_id>/')
api.add_resource(UserDeckCardAPI,'/user/<int:user_id>/<int:deck_id>/<int:card_id>/','/user/<int:user_id>/<int:deck_id>/card/')

if __name__=="__main__":
  app.run()

