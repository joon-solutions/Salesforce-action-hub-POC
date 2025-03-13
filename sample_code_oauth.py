import requests
import json
import os
import base64
from flask import request, Response, redirect
import utils
from dotenv import load_dotenv
load_dotenv()

BASE_DOMAIN = f"https://{os.environ.get('REGION')}-{os.environ.get('PROJECT')}.cloudfunctions.net/{os.environ.get('ACTION_NAME')}-"

IS_PROD = os.environ.get('IS_PROD', '') == 'True'
SALESFORCE_CLIENT_ID = os.getenv('SALESFORCE_CLIENT_ID')
LOOKER_ACTION_CLIENT_ID = os.getenv('LOOKER_ACTION_CLIENT_ID')
LOOKER_ACTION_CLIENT_SECRET = os.getenv('LOOKER_ACTION_CLIENT_SECRET')


auth_url = (f"https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/authorize?response_type=code"
        f"&client_id={SALESFORCE_CLIENT_ID}"
        f"&redirect_uri=https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/token"
    )
# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#actions-list-endpoint
def dev_action_list(request):
    """Return action hub list endpoint data for action"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth

    response = {
        'label': 'Becky Campaign Creator',
        'integrations': [
            {
                'name': os.environ.get('ACTION_NAME'),
                'label': os.environ.get('ACTION_LABEL'),
                'supported_action_types': ['query'],
                "icon_data_uri": "https://github.com/joon-solutions/vertex-ai-actions/blob/main/icons/salesforce_icon.png",
                'form_url': BASE_DOMAIN + 'form',
                'url': BASE_DOMAIN + 'execute',
                'supported_formats': ['json'],
                'supported_formattings': ['formatted'],
                'supported_visualization_formattings': ['noapply'],
                'params': [
                    {
                        'description': "Salesforce domain name, e.g. https://MyDomainName.my.salesforce.com",
                        'label': "Salesforce domain",
                        'name': "salesforce_domain",
                        'required': True,
                        'sensitive': False
                    }
                ],
                'uses_oauth': True
            }
        ]
    }

    print('returning integrations json')
    return Response(json.dumps(response), status=200, mimetype='application/json')

# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#action-form-endpoint
def dev_action_form(request):
    """Return form endpoint data for action"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth

    request_json = request.get_json()
    print(f"request_json: {request_json}")
    # form_params = request_json['form_params']
    state_url = request_json['data']['state_url']
    encrypted_state = utils.encode_state(state_url)
    auth_url_with_state = f"{auth_url}&state={encrypted_state}"
    response_login = [    {
        'name': 'login',
        'type': 'oauth_link',
        'label': 'Log in',
        'description': 'Log in to your Salesforce account.',
        'oauth_url': auth_url_with_state,
    }]
    response_form = [{
            'name': 'campaign_name',
            'label': 'Campaign Name',
            'description': 'Identifying name of the campaign',
            'type': 'text',
            'required': True
        },
            {
            'name': 'start_date',
            'label': 'Start Date',
            'description': "Start date of the campaign",
            'type': 'text',
            'required': True
        }]
    response = response_login
    # if there is a token in the state_json, return the form
    if 'token' in request_json['data']['state_json']:
        response = response_form
        utils.reset_state(request_json['data']['state_url'])
    print(f'returning form json: {json.dumps(response)}')
    return Response(json.dumps(response), status=200, mimetype='application/json')




def dev_action_execute(request):
    """Process form input and send data to Salesforce to create a new campaign"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth
    request_json = request.get_json()
    form_params = request_json['form_params']
    print(f"form_params: {form_params}")
    print(f"request_json: {request_json}")

    if 'token' in request_json['data']['state_json']:
        token = request_json['data']['state_json']['token']
    else:
        return utils.handle_error('No token found in state_json', 400)

    print(f"Mock sending request to Salesforce to create campaign using stored token....")

    # try:
    #     campaign_name = form_params['campaign_name']
    #     start_date = form_params['start_date']
    #     end_date = form_params['end_date']
    #     campaign_status = form_params['campaign_status']
    #     campaign_type = form_params['campaign_type']
    # except KeyError as e:
    #     return utils.handle_error(f"Missing required parameter: {e}", 400)

    # url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/data/v63.0/composite/sobjects"
    # payload = json.dumps({
    #     "allOrNone": False,
    #     "records": [
    #         {
    #             "attributes": {"type": "Campaign"},
    #             "Name": campaign_name,
    #             "StartDate" : start_date,
    #             "EndDate" : end_date,
    #             "Status" : campaign_status,
    #             "Type" : campaign_type
    #         }
    #     ]
    # })

    # headers = {
    #     "Authorization": f"Bearer {token}",
    #     "Content-Type": "application/json"
    # }

    # response = requests.post(url, headers=headers, data=payload, timeout=10)

    # if response.status_code in [200, 201]:
    #     return Response(status=200, mimetype="application/json")
    # else:
    #     return Response(status=response.status_code, mimetype="application/json")
    return Response(status=200, mimetype="application/json")


def dev_action_oauth(request):
    """Return form endpoint data for action"""
    code = request.args.get('code')
    encrypted_state = request.args.get('state')
    state_url = utils.decode_state(encrypted_state)
    request_json = request.get_json()
    print(f"request_json: {request_json}")

    client_id = os.environ.get('SALESFORCE_CLIENT_ID')
    client_secret = os.environ.get('SALESFORCE_CLIENT_SECRET')
    redirect_uri = os.environ.get('SALESFORCE_REDIRECT_URI', 'https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/token')
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri
    }
    headers = {
        # "Content-Type": "application/json"
    }
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/token"
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    print(f"response: {response.json()}")
    print(f"response.status_code: {response.status_code}")
    if response.status_code in [200, 201]:
        token = response.json()['access_token']
        utils.store_state(state_url, {'token': token})
        # return redirect(f"{BASE_DOMAIN}form")
        return Response(response=response, status=response.status_code, mimetype="application/json")

    else:
        return Response(response=response, status=response.status_code, mimetype="application/json")
