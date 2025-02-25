import requests
import json
import os
import base64
import utils
import re

from datetime import datetime
from flask import request, Response, redirect
from icon import icon_data_uri
from dotenv import load_dotenv

load_dotenv()

# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-form-endpoint
def action_task_form(request):
    """Return form endpoint data for action"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth
    
    request_json = request.get_json()
    data = request_json['data']
    print(data)
    
    field_value = ''

    if 'value' in data:
        field_value = data['value']

    response = [{
            'name': 'case_no',
            'label': 'Case Number',
            'description': 'Number of the case',
            'type': 'text',
            'default': field_value,
            'required': True
        },
            {
            'name': 'task_subject',
            'label': 'Task Subject',
            'description': "Subject of the task",
            'type': 'text',
            'required': True
        },
            {
            'name': 'task_status',
            'label': 'Task Status',
            'description': "Status of the task",
            'type': 'select',
            'required': True,
            'options': [
                {'name': 'open', 'label': 'Open'},
                {'name': 'completed', 'label': 'Completed'}
            ]
        },
            {
            'name': 'task_priority',
            'label': 'Task Priority',
            'description': "Priority of the task",
            'type': 'select',
            'required': True,
            'options': [
                {'name': 'normal', 'label': 'Normal'},
                {'name': 'high', 'label': 'High'}
            ]
        }
    ]
    print(f'returning form json: {json.dumps(response)}')
    return Response(json.dumps(response), status=200, mimetype='application/json')




# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-execute-endpoint
def action_task_execute(request):
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
        case_no = form_params['case_no']
        task_subject = form_params['task_subject']
        task_priority = form_params['task_priority']
        task_status = form_params['task_status']
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

    # get object id from case number
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/query/"
    query = f"SELECT Id FROM Case WHERE CaseNumber = '{case_no}'"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.request("GET", url, headers=headers, params={"q": query}, timeout=10)

    if response.status_code in [200, 201] and 'Id' in response:
        records = response.json().get("records", [])
        what_id = records[0].get("Id")
        print(what_id)
    else:
        print(f"No case found for Case Number: {case_no}")
    
    # create task via api
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/composite/sobjects"
    payload = json.dumps({
        "allOrNone": False,
        "records": [
            {
                "attributes": {"type": "Task"},
                "WhatId": what_id,
                "Subject" : task_subject,
                "Priority" : task_priority,
                "Status" : task_status
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
        return Response(status=200, mimetype="application/json")
    else:
        return Response(status=response.status_code, mimetype="application/json", response=json.dumps(response.json()))