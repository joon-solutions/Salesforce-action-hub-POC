import requests
import json
import os
import base64
import utils
import re

from datetime import datetime, timedelta
from flask import request, Response, redirect
from dotenv import load_dotenv

load_dotenv()



BASE_DOMAIN = f"https://{os.environ.get('REGION')}-{os.environ.get('PROJECT')}.cloudfunctions.net/{os.environ.get('ACTION_NAME')}-"

# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-form-endpoint
def task_form(request):
    """Return form endpoint data for action"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth
    
    request_json = request.get_json()
    form_params = request_json['form_params']
    print(form_params)
    data = request_json['data']
    print(data)
    
    cell_value = ''

    if 'value' in data:
        cell_value = data['value']
    
    # get token using username/password
    url = 'https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/token'
    client_id = os.environ.get('SALESFORCE_CLIENT_ID')
    client_secret = os.environ.get('SALESFORCE_CLIENT_SECRET')
    username = os.environ.get('SALESFORCE_USERNAME')
    password = os.environ.get('SALESFORCE_PASSWORD')

    payload = {'grant_type': 'password',
    'client_id': client_id,
    'client_secret': client_secret,
    'username': username,
    'password': password}
    headers = {}

    print(f'payload: {payload}')
    response = requests.request("POST", url, headers=headers, data=payload, timeout = 10)
    print(f'response: {response.json()}')
    token = response.json()['access_token']

    # get category list
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/sobjects/Task/describe"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_task_data = requests.request("GET", url, headers=headers)
    if get_task_data.status_code in [200, 201]:
        task_data = get_task_data.json()
        fields = task_data['fields']
        for field in fields:
                if field["name"] == 'Category__c' and "picklistValues" in field:
                    category_list = [
                        {'name': item['value'], 'label': item['value']}
                        for item in field['picklistValues'] if item["active"]
                    ]
    else:
        print(f"Error {get_task_data.status_code}: {get_task_data.text}")

    #get contact list
    query = f"SELECT Id, Name FROM Contact LIMIT 10"
    url = f"https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/query/?q={query}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_all_contact = requests.request("GET", url, headers=headers)
    if get_all_contact.status_code in [200, 201]:
        contact_data = get_all_contact.json()
        contact_list = [
            {'name': contact['Id'], 'label': contact['Name']}
            for contact in contact_data['records']
        ]
    else:
        print(f"Error {get_all_contact.status_code}: {get_all_contact.text}")


    #get default name for related object
    query = f"SELECT Name FROM Customer_Group__c WHERE Id = '{cell_value}'"
    url = f"https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/query/?q={query}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_related_object_name = requests.request("GET", url, headers=headers)
    if get_related_object_name.status_code in [200, 201]:
        object_name_record = get_related_object_name.json()
        object_name_data = object_name_record['records']
        object_name = object_name_data[0]['Name']
        default_object_list = [{ "name": cell_value, "label": object_name }]
    else:
        print(f"Error {get_related_object_name.status_code}: {get_related_object_name.text}")

    #get other object data list
    query = f"SELECT Id, Name FROM Customer_Group__c LIMIT 10"
    url = f"https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/query/?q={query}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_all_object = requests.request("GET", url, headers=headers)
    if get_all_object.status_code in [200, 201]:
        object_data = get_all_object.json()
        object_list = [
            {'name': object['Id'], 'label': object['Name']}
            for object in object_data['records']
        ]
    else:
        print(f"Error {get_all_object.status_code}: {get_all_object.text}")

    #get own user info
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/userinfo"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_user_info = requests.request("GET", url, headers=headers)
    if get_user_info.status_code in [200, 201]:
        user_data = get_user_info.json()
        user_name = user_data['name']
        user_id = user_data['user_id']
        default_owner_list = [{ "name": user_id, "label": user_name }]
    else:
        print(f"Error {get_user_info.status_code}: {get_user_info.text}")

    #get all user info
    query = f"SELECT Id, Name FROM User LIMIT 10"
    url = f"https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/query/?q={query}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_all_user = requests.request("GET", url, headers=headers)
    if get_all_user.status_code in [200, 201]:
        all_user_data = get_all_user.json()
        user_list = [
            {'name': user['Id'], 'label': user['Name']}
            for user in all_user_data['records']
        ]
    else:
        print(f"Error {get_all_user.status_code}: {get_all_user.text}")

    # get reminder time with 15-min interval
    reminder_time_list = []
    start_time = datetime.strptime("00:00", "%H:%M")  # Start at 12:00 AM

    for i in range(96):  # 96 intervals (24 hours * 4 per hour)
        current_time = start_time + timedelta(minutes=15 * i)
        time_name = current_time.strftime("%H:%M:%S.000Z")  # 24-hour format with milliseconds
        time_label = current_time.strftime("%I:%M %p")  # 12-hour format with AM/PM
        reminder_time_list.append({'name': time_name, 'label': time_label})

    #form configuration
    response = [{
            'name': 'subject',
            'label': 'Subject',
            'type': 'select',
            'required': True,
            'options': [
                {'name': 'Call', 'label': 'Call'},
                {'name': 'Send Letter', 'label': 'Send Letter'},
                {'name': 'Send Quote', 'label': 'Send Quote'},
                {'name': 'Other', 'label': 'Other'}
            ]
        },
            {
            'name': 'contact',
            'label': 'Contact',
            'type': 'select',
            'required': True,
            'options': contact_list
        },
            {
            'name': 'category',
            'label': 'Category',
            'type': 'select',
            'required': True,
            'options': category_list
        },
            {
            'name': 'due_date',
            'label': 'Due Date',
            'description': "Format YYYY-MM-DD",
            'type': 'date',
            'required': True
        },
            {
            'name': 'description',
            'label': 'Description',
            'description': "Tip: Type Command + period to insert quick text.",
            'type': 'textarea',
            'required': True
        },
            {
            'name': 'related_to',
            'label': 'Related To',
            'type': 'select',
            'required': True,
            'options': default_object_list + object_list,
            'default': cell_value   
        },
            {
            'name': 'assigned_to',
            'label': 'Assigned To',
            'type': 'select',
            'required': True,
            'options': default_owner_list + user_list,
            'default': user_id
        },
            {
            'name': 'reminder_date',
            'label': 'Reminder Date',
            'description': "Format YYYY-MM-DD",
            'type': 'text',
            'required': False        
        },
            {
            'name': 'reminder_time',
            'label': 'Reminder Time',
            'type': 'select',
            'required': False,
            'options': reminder_time_list
        }
    ]

    print(f'returning form json: {json.dumps(response)}')
    return Response(json.dumps(response), status=200, mimetype='application/json')




# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-execute-endpoint
def task_execute(request):
    """Process form input and send data to Salesforce to create a new campaign"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth
    request_json = request.get_json()
    form_params = request_json['form_params']
    print(form_params)

    # get token using username/password
    url = 'https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/token'
    client_id = os.environ.get('SALESFORCE_CLIENT_ID')
    client_secret = os.environ.get('SALESFORCE_CLIENT_SECRET')
    username = os.environ.get('SALESFORCE_USERNAME')
    password = os.environ.get('SALESFORCE_PASSWORD')

    validation_errors = {}
    # form params error handling
    try:
        subject = form_params['subject']
        contact = form_params['contact']
        category = form_params['category']
        due_date = form_params['due_date']
        description = form_params['description']
        related_to = form_params['related_to']
        assigned_to = form_params['assigned_to']
    except KeyError as e:
        validation_errors[str(e).strip("'")] = "Missing required parameter"
        response = {
                "looker": {
                    "success": False,
                    "validation_errors": {
                    str(e).strip("'"): "Missing required parameter"
                    }
                }
            }
        
    if not bool(re.match(r"^\d{4}-\d{2}-\d{2}$", due_date)):
        validation_errors['due_date'] = "Invalid date format. Please use YYYY-MM-DD format" 
    if validation_errors:
        response = {
            "looker": {
                "success": False,
                "validation_errors": validation_errors
            }
        }
        return Response(status=400, mimetype="application/json", response=json.dumps(response))


    payload = {'grant_type': 'password',
    'client_id': client_id,
    'client_secret': client_secret,
    'username': username,
    'password': password}
    headers = {}

    print(f'payload: {payload}')
    response = requests.request("POST", url, headers=headers, data=payload, timeout = 10)
    print(f'response: {response.json()}')
    token = response.json()['access_token']

    #get email of owner
    query = f"SELECT Email FROM User WHERE Id = '{assigned_to}'"
    url = f"https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/query/?q={query}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_owner_email = requests.request("GET", url, headers=headers)
    if get_owner_email.status_code in [200, 201]:
        email_data = get_owner_email.json()
        all_owner_data = email_data['records']
        owner_email = all_owner_data[0]['Email']
        print(owner_email)
    else:
        print(f"Error {get_owner_email.status_code}: {get_owner_email.text}")
 
    # create task via api
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/composite/sobjects"
    if 'reminder_date' in form_params and 'reminder_time' in form_params:
        reminder_date = form_params['reminder_date']
        reminder_time = form_params['reminder_time']
        payload = json.dumps({
        "allOrNone": False,
        "records": [
            {
                "attributes": {"type": "Task"},
                "Subject" : subject,
                "WhoId" : contact,
                "Category__c" : category,
                "ActivityDate":  due_date,
                "Description" : description,
                "WhatId" : related_to,
                "OwnerId" : assigned_to,
                "IsReminderSet": "true",
                "ReminderDateTime": f"{reminder_date}T{reminder_time}",
                "RecordTypeId":"0122w000001MHouAAG"
            }
        ]
    })
    else:
        payload = json.dumps({
        "allOrNone": False,
        "records": [
            {
                "attributes": {"type": "Task"},
                "Subject" : subject,
                "WhoId" : contact,
                "Category__c" : category,
                "ActivityDate":  due_date,
                "Description" : description,
                "WhatId" : related_to,
                "OwnerId" : assigned_to,
                "RecordTypeId":"0122w000001MHouAAG"
            }
        ]
    })

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f'create task payload: {payload}')
    print(f'create task headers: {headers}')
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    print(f'create task response: {response.json()}')
    print(f'create task response status: {response.status_code}')
    if response.status_code in [200, 201] and response.json()[0]['success']:
        send_task_gchat(subject, due_date, owner_email)
        return Response(status=200, mimetype="application/json")
    else:
        return Response(status=response.status_code, mimetype="application/json", response=json.dumps(response.json()))
    

#url hard coded for now. This solution does not allow @users, we would need to move to chat api for this (which if this is adopted will be the solution we use)
#todo: pass in url to created salesforce task, and embed in the card in the button link
def send_task_gchat(subject, due_date, owner_email):
    if owner_email:
        card_body = json.dumps(
            {
                "cardsV2": [
                    {
                        "cardId": "salesforceTaskCard",
                        "card": {
                            "header": {
                                "title": "New Salesforce Task Assigned!",
                                "subtitle": "Click to view details.",
                                "imageUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABC0lEQVQ4jaXTL0vDURjF8c/zQ0RETCJG2RbE4GsYJjGbDT+LwVdgFLOYBfcCjGI2GUxiMI2tGERERERERHwMczD/4rYDF275nuce7nkiM8MQKoaBYaR7if3WCFERWSGauJQIE+RLlrWnnwwiMyMa7VFsYQPjeEQDk1jEFXZwiFE8Z1l97TVYko7En5HucYIpNGXu5lrtvGuwjc0+41+j3p141ycMM1gvotGe1ck+gHK+wApmBzOIiwJjg8FusFfgCA//hG5xjgNyOctqs/sLdZRY+Di9usZrB85N4hSPn3oAsd8qUBFxiLmeias40ynPt5fG12WKRnsaSzqNPEYry+rbb5m+GfSrobfxHWu4YtTFW9MMAAAAAElFTkSuQmCC",
                                "imageType": "CIRCLE",
                            },
                            "sections": [
                                {
                                    "widgets": [
                                        {
                                            "textParagraph": {
                                                "text": f"Hey {owner_email}, a new Salesforce task has been assigned to you!"
                                            }
                                        },
                                        {
                                            "decoratedText": {
                                                "topLabel": "Task Subject",
                                                "text": f"{subject}",
                                                "wrapText": True,
                                            }
                                        },
                                        {
                                            "decoratedText": {
                                                "topLabel": "Due Date",
                                                "text": f"{due_date}",
                                            }
                                        },
                                        {
                                            "buttonList": {
                                                "buttons": [
                                                    {
                                                        "text": "View Task in Salesforce",
                                                        "onClick": {
                                                            "openLink": {
                                                                "url": "SALESFORCE_TASK_URL"
                                                            }
                                                        },
                                                    }
                                                ]
                                            }
                                        },
                                    ]
                                }
                            ],
                        },
                    }
                ]
            }
        )
        headers = {
            "Content-Type": "application/json"
        }
        url = "https://chat.googleapis.com/v1/spaces/AAAAXHq00t0/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=rI4xW7AtuAC9FSZhBdpLDAs7koLmtQ9lSvi3aFIixzg"
        try:
            requests.post(url, headers=headers, data=card_body, timeout=10)
        #do not really care if this fails right now as its poc, no specific error handling, but will log error.
        except Exception as e:
            print(f"Error sending google chat: {e}")