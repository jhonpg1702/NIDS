from flask import Flask,request

from config import Config
from flask_sqlalchemy import SQLAlchemy

from flask_sse import sse



import subprocess
import os ,signal


db = SQLAlchemy()

flows = []
resp = {}
pid = None
interface = ''
basedir = os.path.abspath(os.path.dirname(__file__))
def cicflowmeter(start,interface):
    global pid
    if start: 
        p = subprocess.Popen(["cicflowmeter","-i",
                            interface,"-c",
                            os.path.join(basedir, 'static/flows.csv') ,
                            "-u",
                            request.url_root+"predict/"]) 
        pid = p.pid
        print(pid,start,p)    

    elif not start:        
        os.kill(pid, signal.SIGSTOP)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():

        from app import routes

        app.register_blueprint(sse, url_prefix='/stream')
        # app.register_blueprint(routes)


        db.create_all()


    return app
