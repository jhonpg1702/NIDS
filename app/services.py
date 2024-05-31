import requests

import json
import time
import re
from datetime import datetime,timedelta
from flask import Blueprint, redirect, render_template, url_for,flash,json,request
from sqlalchemy import func,update
from concurrent.futures import ThreadPoolExecutor
import os
from flask import current_app as app
from app.funcionesChatbot import *
from . import cicflowmeter


def obtener_Mensaje_whatsapp(message):

    
        if 'type' not in message:
            return 'mensaje no reconocido'

        typeMessage = message['type']

        if typeMessage == 'request_welcome':
            text ="request_welcome"

        elif typeMessage == 'text':
            text = message['text']['body']

        elif typeMessage == 'button':
            text = message['button']['text']

        elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
            text = message['interactive']['list_reply']['title']
        elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
            text = message['interactive']['button_reply']['title']

        return text


# -----------------------
#    funciones chatbot
# --------------------------- 

def administrar_chatbot(text,number, messageId,type):
    try:
        number_without_prefix = number.replace('57', '', 1)  # Quita el prefijo '57' una vez


        text = text.lower() #mensaje que envio el usuario
        list = []
        print("mensaje del usuario: ",text)



        markRead = markRead_Message(messageId)
        list.append(markRead)
        time.sleep(2)


        # Expresiones regulares para detectar diferentes tipos de saludos
        saludos_patterns = ["hola", "buenos días", "buenas tardes", "buenas noches", "qué tal", "saludos", 
                        "cómo estás", "hola equipo", "buen día", "buenas", "hola a todos", "buen día a todos",
                        "hola amigos", "saludos cordiales","menu" ,"menú","oe"]
        regex_saludos = '|'.join(saludos_patterns)

        if re.search(regex_saludos, text)  or "menú principal" in text:

            listReply = crear_mensaje_menu(number, messageId)

            list.append(listReply)
        elif "1. " in text  :
            document = document_Message(number, sett.document_url, "lista_atacantes.csv")
            enviar_Mensaje_whatsapp(document)

        elif "2." in text  :
            body = "Se estan bloqueando las ip maliciosas espera un momento"        
            mensaje = text_Message(number, body)

            enviar_Mensaje_whatsapp(mensaje)
            time.sleep(5)
            
            body = "Se bloquearon las ip maliciosas correctamente ✅"        
            mensaje = text_Message(number, body)

            enviar_Mensaje_whatsapp(mensaje)
            time.sleep(3)

        elif "3." in text  :
            body = "Se detuvo el servidor ⛔"        
            mensaje = text_Message(number, body)
            list.append(mensaje)
            cicflowmeter(False,None)
            



        for item in list:
            enviar_Mensaje_whatsapp(item)


    except Exception as e:
        print(f"Se produjo un error: {e}")




def crear_mensaje_menu(number, messageId):
    body = ("¡Atención urgente 🚨 Estamos experimentando un ataque a nuestro servidor.\n\n"
        "Necesitamos tu ayuda para mitigar este incidente. Por favor, selecciona una de las siguientes opciones para contribuir:\n")

    options, descriptions = crear_opciones_menu()
    footer = ""
    listReply = listReply_Message(number, options, body, footer, "sed1", messageId, descriptions)
    return listReply

def crear_opciones_menu():

    options = ["1. Lista  📑", "2. Bloquear ❌", "3. Detener 📛"]
    descriptions = ["Muestra la lista de los atacantes", "Bloquea las ip maliciosas", "Detener el servidor"]


    return options,descriptions



            



