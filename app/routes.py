from flask import render_template,flash,redirect,url_for,request, session,  Response
from flask import request,json,jsonify, Response
from sklearn import metrics
from flask_sse import sse
import psutil
import netifaces
import json
import os
import subprocess
import sys
import numpy as np
import pandas as pd 

import pickle
import os, signal
from app.forms import If_form
# from app import app,db
from app.models import *
from app import sett
from app import services
from app.services import *
from . import cicflowmeter

flows = []
resp = {}
pid = None
interface = ''
basedir = os.path.abspath(os.path.dirname(__file__))




@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.webhook_token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        type = message['type']
        number = message['from']
        number_without_prefix = number.replace('57', '', 1)  # Quita el prefijo '57' una vez
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        
        text = services.obtener_Mensaje_whatsapp(message)
        services.administrar_chatbot(text, number, messageId,type)
        print("/////////////////////////",body)

        return 'enviado'

    except Exception as e:
        print(str(e))
        return 'no enviado ' + str(e)

@app.route('/',methods=['POST','GET'])          
def index():
       interface = netifaces.interfaces()
       form = If_form()
       print("request.url",request.url)
       interface.insert(0,"-- Please Select Interface --")
       form.interface.choices = interface
       form.interface.default = interface[0]
       
       ifconfig = subprocess.check_output(['ifconfig'])

       return render_template('interface.html', form = form, ifconfig = ifconfig)
       
# def cicflowmeter(start,interface):
#     global pid
#     if start: 
#         p = subprocess.Popen(["cicflowmeter","-i",
#                             interface,"-c",
#                             os.path.join(basedir, 'static/flows.csv') ,
#                             "-u",
#                             request.url_root+"predict/"]) 
#         pid = p.pid
#         print(pid,start,p)    

#     elif not start:        
#         os.kill(pid, signal.SIGSTOP)
        

@app.route('/start',methods=['POST','GET'])          
def start():
        form = If_form();      
        cicflowmeter(True,form.interface.data)
        print(form.interface.data)
        session['interface'] = form.interface.data
        return redirect(url_for('home'))


@app.route('/ip', methods=['GET'])
def ip():
    ip = request.args.get('ip')
    if request.method == 'GET':
        whois = subprocess.check_output([f'whois {ip}'],shell=True)
        print("whois",whois)
        # traceroute = subprocess.check_output([f'traceroute  {ip}'],shell=True)        
        message = {'whois': whois.decode("utf-8")}
        return jsonify(message)  # serialize and use JSON headers


@app.route('/newInterface')
def newInterface():
    cicflowmeter(False,None)
    return redirect(url_for('index'))


@app.route('/stop')
def stop():
    cicflowmeter(False,None)
    print("Stop")
    return ('', 204)

model = pickle.load(open(os.path.join(basedir, 'nids_model.pkl'),"rb"))


class PandasEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            return obj.to_dict()
        elif isinstance(obj, pd.Index):
            return obj.tolist()
        return super().default(obj)
    
@app.route('/predict/', methods=['POST'])
def predict():
    result = User.query.filter_by(username="jhon").first()

    req = request.get_json()
    # print("req",req)
    df1 = pd.DataFrame(data=req["data"], columns=req["columns"] )
    df2 = df1.copy()
    cols = [' Bwd Packet Length Std', ' min_seg_size_forward', ' PSH Flag Count',
            ' Min Packet Length',' Init_Win_bytes_backward', ' ACK Flag Count', 
            'Total Length of Fwd Packets', ' Subflow Fwd Bytes',
            'Init_Win_bytes_forward', ' Bwd Packet Length Min', ' Fwd IAT Std',
            ' Flow IAT Max', ' URG Flag Count',' Destination Port', ' Flow IAT Mean',
            ' Flow Duration', ' Bwd Packets/s', 'Fwd IAT Total', 'Bwd IAT Total', 
            ' act_data_pkt_fwd', ' Down/Up Ratio', ' Idle Min', ' Fwd Packet Length Min', 
            ' Bwd IAT Max', ' Fwd Packet Length Mean']
    feature = df1[cols]

    # Making Pridiction
    pred = model.predict(feature) 
    label = pred[0]

    if label == 0:
        df1['label'] = 'Benign'
    elif label == 1:
        result.ataque = True
        if result.ataque == True:
            if result.whatsapp == False:
                listReply = crear_mensaje_menu("573133268392", "")
                enviar_Mensaje_whatsapp(listReply)
                result.whatsapp = True
                
        db.session.commit()


        df1['label'] = 'Bot'

    elif label == 2:
        df1['label'] = 'DDoS'
    elif label == 3:
        df1['label'] = 'Infilteration'
    elif label == 4:
        df1['label'] = 'PortScan'
    elif label == 5:
        df1['label'] = 'Brute-Force'
    elif label == 6:
        df1['label'] = 'Sql-Injection'
    elif label == 7:
        df1['label'] = 'XSS'

    df1.rename(columns = {" Destination Port": "dst_port"}, 
        inplace = True)

    # result = df1.to_json(orient="records")    
    result= json.dumps(df1, cls=PandasEncoder)
    # print("result",result)
    sse.publish(result, type='greeting')
    resp = {"label" :  df1['label'].values[0]}
    # print(resp)
    return jsonify(resp)

@app.route('/home')
def home():    
    return render_template('home.html')


@app.route('/testing')
def testing():
    benign = 0
    bot = 0
    ddos = 0
    portScan = 0
    infliteration = 0
    bruteForce = 0
    sqlInjection = 0
    xss = 0
    total = 0
    df = pd.read_csv(os.path.join(basedir, 'smt_X_Test.csv'))
    y_test = pd.read_csv(os.path.join(basedir, 'smt_y_Test.csv'))
    df.drop('Unnamed: 0',
    axis='columns', inplace=True)
    pred = model.predict(df)    
    # (unique, counts) = np.unique(pred, return_counts=True)
    accuracy = metrics.accuracy_score(y_test["0"].values.reshape(-1, 1),pred)

    for x in pred:
        total += 1
        if x == 0:
            benign += 1
        elif x == 1:
            bot += 1          
        elif x == 2:
            ddos += 1
        elif x == 3:
            infliteration += 1
        elif x == 4:
            portScan += 1
        elif x == 5:
            bruteForce += 1
        elif x == 6:
            sqlInjection += 1
        elif x == 7:
            xss += 1

    accuracy = accuracy*100

    result = {"accuracy" : accuracy,
                "benign": benign, "bot" : bot, "total" : total,
                "ddos":ddos,"infliteration": infliteration,
                "portscan" : portScan,"bruteforce": bruteForce,"sqlInjection":sqlInjection,"xss":xss}

    print(result)

    return render_template('testing.html', result = result)
