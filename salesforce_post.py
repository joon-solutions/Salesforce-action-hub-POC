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


# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-form-endpoint
def post_form(request):
    """Return form endpoint data for action"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth

    request_json = request.get_json()
    print(f"INPUT:{request_json}")
    data = request_json['data']
    state_url = data['state_url']
    
    cell_value = ''

    if 'value' in data:
        cell_value = data['value']
        
    # oauth
    client_id = os.environ.get('SALESFORCE_CLIENT_ID')
    redirect_uri = os.environ.get('SALESFORCE_REDIRECT_URI')
    auth_url = (f"https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/authorize?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        )
    encrypted_state = utils.encode_state(state_url)
    auth_url_with_state = f"{auth_url}&state={encrypted_state}"

    response_login = [    {
        'name': 'login',
        'type': 'oauth_link',
        'label': 'Log in',
        'description': 'Log in to your Salesforce account.',
        'oauth_url': auth_url_with_state,
    }]

    state_json = json.loads(data['state_json'])

    if 'token' in state_json:
        token = state_json.get('token')
        # get proposal mentions: https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_resources_mentions_completions.htm
        url = f"https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/chatter/mentions/completions?contextId={cell_value}&q=a"
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
            utils.reset_state(data['state_url'])
            print(f"Error {get_proposal_mentions.status_code}: {get_proposal_mentions.text}")  

        response_form = [{
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
        response = response_form
    else:
        response = response_login
    
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

    state_json = json.loads(data['state_json'])

    if 'token' in state_json:
        token = state_json.get('token')
    else:
        return utils.handle_error('No token found in state_json', 400)
    
    cell_value = ''

    if 'value' in data:
        cell_value = data['value']

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
        utils.reset_state(data['state_url'])
        return Response(status=response.status_code, mimetype="application/json", response=json.dumps(response.json()))
    