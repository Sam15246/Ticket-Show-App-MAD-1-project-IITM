# --------------------  Imports  --------------------
import os
from flask import Flask

from flask_restful import Api

from application.config import LocalDevelopmentConfig
from application.database import db
from flask_cors import CORS

# --------------------  Initialization  --------------------
app = None
api = None

def create_app():

    app = Flask(__name__, template_folder="templates")
    CORS(app)

    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Staring Local Development")
        app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)

    api = Api(app)

    app.app_context().push()
    
    return app, api 


app, api = create_app()

# Importing all the controllers so they are loaded
'''If this line is put at the start(i.e. if it is executed 
before the creation of the Flask instance), it will create a 
problem related to app.app_context'''
from application.controllers import *

# Importing all the restful controllers
from application.api import *


# --------------------  Adding the resources to the API --------------------
api.add_resource(ShowApi, '/api/show/<int:show_id>','/api/show')
api.add_resource(VenueApi, '/api/venue/<int:venue_id>','/api/venue')
api.add_resource(ShowDisplayApi, '/api/show/<int:show_id>/display')
api.add_resource(VenueDisplayApi, '/api/venue/<int:venue_id>/display')

# --------------------  Main  --------------------
if __name__ == "__main__":

    app.run(debug=True)
# --------------------  End  --------------------




