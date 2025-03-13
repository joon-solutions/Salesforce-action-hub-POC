import requests
import json
import os
import base64
import utils
import re

from datetime import datetime
from flask import request, Response, redirect
from dotenv import load_dotenv

load_dotenv()



BASE_DOMAIN = f"https://{os.environ.get('REGION')}-{os.environ.get('PROJECT')}.cloudfunctions.net/{os.environ.get('ACTION_NAME')}-"

# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-form-endpoint
def post_form(request):
    """Return form endpoint data for action"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth

    request_json = request.get_json()
    data = request_json['data']
    
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

    # get proposal mentions: https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_resources_mentions_completions.htm
    url = f"https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/chatter/mentions/completions?contextId={cell_value}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_proposal_mentions = requests.request("GET", url, headers=headers)
    if get_proposal_mentions.status_code in [200, 201]:
        proposal_mention_data = get_proposal_mentions.json()
        proposal_mention_list = [
            {'name': proposal_mention['recordId'], 'label': proposal_mention['name']}
            for proposal_mention in proposal_mention_data['mentionCompletions']
        ]
    else:
        print(f"Error {get_proposal_mentions.status_code}: {get_proposal_mentions.text}")  

    response = [{
            'name': 'content',
            'label': 'Content',
            'description': "Share an update",
            'type': 'textarea',
            'required': True
        },
            {
            'name': 'mention',
            'label': 'Mention',
            'description': "Notify a person or group about this update.",
            'type': 'select',
            'required': False,
            'options': proposal_mention_list
        }
    ]
    print(f'returning form json: {json.dumps(response)}')
    return Response(json.dumps(response), status=200, mimetype='application/json')




# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-execute-endpoint
def post_execute(request):
    """Process form input and send data to Salesforce to create a new campaign"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth
    request_json = request.get_json()
    form_params = request_json['form_params']
    data = request_json['data']
    
    print(form_params)
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

    validation_errors = {}
    # form params error handling
    try:
        content = form_params['content']
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
    
    # create chatter via api
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/chatter/feed-elements/"
    if 'mention' in form_params:
        mention = form_params['mention']
        payload = json.dumps(
            { 
            "body" : {
                "messageSegments" : [
                  {
                    "type" : "Text",
                    "text" : content
                  },
                  {
                    "type" : "Text",
                    "text" : " "
                  },
                  {   
                    "type" : "Mention",
                    "id" : mention
                  }
                ]
            },
            "feedElementType" : "FeedItem",
            "subjectId" : cell_value
            }
        )
    else:
        payload = json.dumps(
            { 
            "body" : {
               "messageSegments" : [
                     {
                         "type" : "Text",
                         "text" : content
                     }
                ]
             },
            "feedElementType" : "FeedItem",
            "subjectId" : cell_value
            }
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f'create chatter payload: {payload}')
    print(f'create chatter headers: {headers}')
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    print(f'create chatter response: {response.json()}')
    print(f'create chatter response status: {response.status_code}')
    if response.status_code in [200, 201]:
        return Response(status=200, mimetype="application/json")
    else:
        return Response(status=response.status_code, mimetype="application/json", response=json.dumps(response.json()))
    