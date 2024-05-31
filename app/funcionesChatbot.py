import requests
from app import sett
import json
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from flask import Blueprint, redirect, render_template, url_for,flash,json,request,session
from flask import current_app as app

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + sett.whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            print( response.text)
            return 'error al enviar mensaje', response.status_code
            
    except Exception as e:
        print(e)
        return e,403

    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )
        # print(buttons,"  "+i)
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data


def listReply_Message(number, options, body, footer, sedd,messageId,descriptions):

    rows = []
    for i, (option, description) in enumerate(zip(options, descriptions)):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": description
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data





def document_Message(number, url, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "filename": filename
            }
        }
    )
    return data
def image_Message(number, url):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "image",
            "image": {
                "link": url,
            }
        }
    )
    return data

def video_Message(number, url):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "video",
            "video": {
                "link": url,
            }
        }
    )
    return data

def audio_Message(number, url):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "audio",
            "aduio": {
                "link": url,
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data 


# -----------------------
#    api tv sanjorge consultas 
# --------------------------- 

def buscar_servicio(texto, servicios):
    palabras = texto.split()
    for servicio in servicios:
        coincide = True
        for palabra in palabras:
            if servicio['id']!= int(palabra) and servicio['nombre_tipo_servicio'].lower()!= palabra.lower():
                coincide = False
                break
        if coincide:
            return servicio
    return None


def procesar_respuesta_facturacion(response_tercer_solicitud):
    # Imprimir la respuesta JSON
    print("Respuesta de la tercera solicitud:")
    print(response_tercer_solicitud)
    # Comprobar si hay información de facturación
    items = response_tercer_solicitud.json()["data"]["items"]
    print(items)
    if not items:
        return {"consulta": 0, "mensaje": "No hay información de facturación"}

    # Obtener la fecha actual
    fecha_actual = str(datetime.now().date())

    # Acceder a las fechas de vencimiento desde la respuesta JSON y convertirlas a objetos datetime
    vencimientos = [datetime.strptime(item["vencimiento"], "%Y-%m-%dT%H:%M:%S.%fZ") for item in items]

    # Obtener solo la fecha como cadena
    fechas_vencimiento = [fecha.strftime("%Y-%m-%d") for fecha in vencimientos]

    # Obtener los valores correspondientes
    valores = [item["valor"] for item in items]

    # Determinar el valor y la fecha de vencimiento a retornar
    valor_retornar = ""
    fecha_retornar = ""
    for fecha_vencimiento, valor in zip(fechas_vencimiento, valores):
        if fecha_actual <= fecha_vencimiento:
            valor_retornar = valor
            fecha_retornar = fecha_vencimiento
            break

    # Caso especial: si la fecha actual es posterior a todos los vencimientos
    if not valor_retornar:
        print("entro")
        valor_retornar = valores[0]
        fecha_vencimiento_dt = vencimientos[0]
        # Sumar un mes
        nueva_fecha = fecha_vencimiento_dt + relativedelta(months=1)
        fecha_retornar = nueva_fecha.strftime("%Y-%m-%d")

    print("///////////////////", valor_retornar, fecha_retornar)
    return {"valor": valor_retornar, "fecha": fecha_retornar}


def consulta_factura(cedula):
    token = app.config['LLAVE_TOKEN_TVSANJORGE']
    # URL de la API y el parámetro nuip
    url = f"https://crm.tvsanjorge.co/api/autogestion/cliente?nuip={cedula}"

    # Encabezado con el token de autenticación
    headers = {
        "x-token-auth": token
    }
    print(cedula)
    # # Parámetros de la solicitud
    # params = {
    #     "nuip": cedula
    # }

    # Realizar la solicitud GET con los parámetros y encabezados
    response = requests.get(url, headers=headers)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Imprimir la respuesta en formato JSON
        print("Respuesta de la primera solicitud:")

        # print(response.json())
        nombre = response.json()["data"]["nombre"]
        apellido = response.json()["data"]["apellido"]
        # URL de la segunda solicitud utilizando el _id obtenido
        # Almacenar los datos en la sesión
        nombre_completo = nombre+" "+apellido



        id_cliente = response.json()["data"]["_id"]
        # URL de la segunda solicitud utilizando el _id obtenido

        url_segunda_solicitud = f"https://crm.tvsanjorge.co/api/autogestion/servicios?cliente={id_cliente}"
        # Parámetros para la segunda solicitud


        # Realizar la segunda solicitud GET con el _id como parámetro
        response_segunda_solicitud = requests.get(url_segunda_solicitud, headers=headers)

        # Verificar si la segunda solicitud fue exitosa (código de estado 200)
        if response_segunda_solicitud.status_code == 200:
            # Imprimir la respuesta JSON
            print("Respuesta de la segunda solicitud:")
            # print(response_segunda_solicitud.json())

            # Obtener la lista de servicios de la respuesta JSON
            servicios = response_segunda_solicitud.json()["data"]

            # Contar cuántos _id hay en la respuesta
            count_ids = len(servicios)
            print(f"Número de _id en la respuesta: {count_ids}")
            # Si hay al menos un servicio, utilizar el primer _id para la tercera solicitud
            id_servicios = []
            if count_ids > 1:
                for i, servicio in enumerate(servicios, start=1):
                    id_servicios.append({
                        "id": i,
                        "id_servicio": servicio["_id"],
                        "nombre_tipo_servicio": servicio["tipoServicio"]["nombre"],
                        "barrio": servicio["barrio"]
                    })
                    print(id_servicios)
                app.config['servicios'] = id_servicios 
                return {"consulta":2,"servicios":id_servicios,"nombre":nombre_completo}
            
            else:
                id_servicio = servicios[0]["_id"]

                # id_cliente = response_segunda_solicitud.json()["data"][0]["_id"]

                url_tercer_solicitud = f"https://crm.tvsanjorge.co/api/autogestion/facturacion?servicio={id_servicio}"

                # Realizar la segunda solicitud GET con el _id como parámetro
                response_tercer_solicitud = requests.get(url_tercer_solicitud, headers=headers)

            # Verificar si la segunda solicitud fue exitosa (código de estado 200)
            if response_tercer_solicitud.status_code == 200:
                # Imprimir la respuesta JSON
                print("Respuesta de la tercera solicitud:")
                # print(response_tercer_solicitud.json())
                if not response_tercer_solicitud.json()["data"]["items"]:
                    return {"consulta":0, "mensaje": "No hay información de facturación"}
                else:
                    resultado = procesar_respuesta_facturacion(response_tercer_solicitud)

                    return {"consulta":1,"valor": resultado['valor'], "fecha": resultado['fecha'],"nombre":nombre_completo}

            else:

                print("Error en la segunda solicitud:", response_segunda_solicitud.status_code)
        else:
            print("Error en la segunda solicitud:", response_segunda_solicitud.status_code)

    else:
        # Si la solicitud falla, imprimir el código de estado
        print("Error:", response.status_code)

        return {"consulta":0, "mensaje": "Lo siento, el número ingresado no está registrado. Puedes verificarlo e intentarlo nuevamente."}
    
def consulta_factura_id(id_servicio):
    token = app.config['LLAVE_TOKEN_TVSANJORGE']
    # URL de la API y el parámetro nuip
    url =  f"https://crm.tvsanjorge.co/api/autogestion/facturacion?servicio={id_servicio}"
    print(id_servicio)
    # Encabezado con el token de autenticación
    headers = {
        "x-token-auth": token
    }

    # Realizar la solicitud GET con los parámetros y encabezados
    response = requests.get(url, headers=headers)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Imprimir la respuesta en formato JSON
        print("Respuesta de la primera solicitud:")
        resultado = procesar_respuesta_facturacion(response)

        return {"consulta":1,"valor": resultado['valor'], "fecha": resultado['fecha']}

    else:
        # Si la solicitud falla, imprimir el código de estado
        print("Error:", response.status_code)

        return {"consulta":0, "mensaje": "Lo siento, el número ingresado no está registrado."}


def enviar_factura(cedula):
    token = app.config['LLAVE_TOKEN_TVSANJORGE']
    # URL de la API y el parámetro nuip
    url = f"https://crm.tvsanjorge.co/api/autogestion/cliente?nuip={cedula}"

    # Encabezado con el token de autenticación
    headers = {
        "x-token-auth": token
    }
    print(cedula)


    # Realizar la solicitud GET con los parámetros y encabezados
    response = requests.get(url, headers=headers)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Imprimir la respuesta en formato JSON
        print("Respuesta de la primera solicitud:")

        # print(response.json())

        nombre = response.json()["data"]["nombre"]
        apellido = response.json()["data"]["apellido"]
        # URL de la segunda solicitud utilizando el _id obtenido
        # Almacenar los datos en la sesión
        nombre_completo = nombre+" "+apellido

        app.config['nombre'] = nombre_completo 
        app.config['cedula'] = cedula 

        # return {"consulta":True,"nombre": nombre_completo}
        id_cliente = response.json()["data"]["_id"]
        # URL de la segunda solicitud utilizando el _id obtenido

        url_segunda_solicitud = f"https://crm.tvsanjorge.co/api/autogestion/servicios?cliente={id_cliente}"

        # Realizar la segunda solicitud GET con el _id como parámetro

        response_segunda_solicitud = requests.get(url_segunda_solicitud, headers=headers)
        # Verificar si la segunda solicitud fue exitosa (código de estado 200)
        if response_segunda_solicitud.status_code == 200:
            # Imprimir la respuesta JSON
            print("Respuesta de la segunda solicitud:")
            # print(response_segunda_solicitud.json())

            # Obtener la lista de servicios de la respuesta JSON
            servicios = response_segunda_solicitud.json()["data"]

            # Contar cuántos _id hay en la respuesta
            count_ids = len(servicios)
            print(f"Número de _id en la respuesta: {count_ids}")
            # Si hay al menos un servicio, utilizar el primer _id para la tercera solicitud
            id_servicios = []
            if count_ids > 1:
                for i, servicio in enumerate(servicios, start=1):
                    id_servicios.append({
                        "id": i,
                        "id_servicio": servicio["_id"],
                        "nombre_tipo_servicio": servicio["tipoServicio"]["nombre"],
                        "barrio": servicio["barrio"],
                        "codigo":servicio["codigo"]
                        
                    })
                    print(id_servicios)
                app.config['servicios_comprobante'] = id_servicios 
                return {"consulta":2,"servicios":id_servicios,"nombre":nombre_completo}
            
            else:
                codigo = servicios[0]["codigo"]
 
                
                return {"consulta":1,"nombre": nombre_completo,"codigo":codigo}




    else:
        # Si la solicitud falla, imprimir el código de estado
        print("Error:", response.status_code)

        return {"consulta":False, "mensaje": "Lo siento, el número ingresado no está registrado. Puedes verificarlo e intentarlo nuevamente."}


# def plantilla_enviar_factura(number,nombre,cedula,id_factura):
#     fecha_actual = datetime.now().date()
#     fecha_actualR = fecha_actual.strftime("%Y-%m-%d")
#     data = json.dumps(
#         {
#         "messaging_product": "whatsapp",
#         "to": number,
#         "type": "template",
#         "template": {
#             "name": "cliente_factura",
#             "language": {
#             "code": "es"
#             },
#             "components": [
#             {
#                 "type": "header",
#                 "parameters": [
#                 {
#                     "type": "image",
#                     "image": {
#                     "link": sett.recibe_url_folder_img + id_factura
#                     }
#                 }
#                 ]
#             },
#             {
#                 "type": "body",
#                 "parameters": [
#                 {
#                     "type": "text",
#                     "text": nombre
#                 },
#                 {
#                     "type": "text",
#                     "text": cedula
#                 },
#                 {
#                     "type": "text",
#                     "text": fecha_actualR
#                 }

#                 ]
#             },

#             ]
#         }
#         }


        
#     ) 
#     return data
