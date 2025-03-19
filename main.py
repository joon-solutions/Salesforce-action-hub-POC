import requests
import json
import os
import base64
import utils
import re
from urllib.parse import urlencode
from datetime import datetime
from flask import request, Response, redirect
from dotenv import load_dotenv

from .salesforce_campaign import campaign_form, campaign_execute
from .salesforce_poll import poll_form, poll_execute
from .salesforce_post import post_form, post_execute
from .salesforce_question import question_form, question_execute
from .salesforce_task import task_form, task_execute

load_dotenv()



BASE_DOMAIN = f"https://{os.environ.get('REGION')}-{os.environ.get('PROJECT')}.cloudfunctions.net/{os.environ.get('ACTION_NAME')}-"

# https://github.com/looker-open-source/actions/blob/master/docs/action_api.md#actions-list-endpoint
def salesforce_action_list(request):
    """Return action hub list endpoint data for action"""
    auth = utils.authenticate(request)
    if auth.status_code != 200:
        return auth

    response = {
        'label': 'POC Action Hub',
        'integrations': [
            {
                'name': os.environ.get('ACTION_NAME'),
                'label': os.environ.get('ACTION_LABEL'),
                'supported_action_types': ['cell'],
                "icon_data_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABC0lEQVQ4jaXTL0vDURjF8c/zQ0RETCJG2RbE4GsYJjGbDT+LwVdgFLOYBfcCjGI2GUxiMI2tGERERERERHwMczD/4rYDF275nuce7nkiM8MQKoaBYaR7if3WCFERWSGauJQIE+RLlrWnnwwiMyMa7VFsYQPjeEQDk1jEFXZwiFE8Z1l97TVYko7En5HucYIpNGXu5lrtvGuwjc0+41+j3p141ycMM1gvotGe1ck+gHK+wApmBzOIiwJjg8FusFfgCA//hG5xjgNyOctqs/sLdZRY+Di9usZrB85N4hSPn3oAsd8qUBFxiLmeias40ynPt5fG12WKRnsaSzqNPEYry+rbb5m+GfSrobfxHWu4YtTFW9MMAAAAAElFTkSuQmCC",
                'form_url': BASE_DOMAIN + 'form',
                'url': BASE_DOMAIN + 'execute',
                'supported_formats': ['json', 'csv_zip'],
                'required_fields': [{"any_tag": ["sfdc_lead_id"]}],
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
            },
            {
                'name': 'salesforce-post-creator-poc',
                'label': 'Post',
                'supported_action_types': ['cell'],
                "icon_data_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABC0lEQVQ4jaXTL0vDURjF8c/zQ0RETCJG2RbE4GsYJjGbDT+LwVdgFLOYBfcCjGI2GUxiMI2tGERERERERHwMczD/4rYDF275nuce7nkiM8MQKoaBYaR7if3WCFERWSGauJQIE+RLlrWnnwwiMyMa7VFsYQPjeEQDk1jEFXZwiFE8Z1l97TVYko7En5HucYIpNGXu5lrtvGuwjc0+41+j3p141ycMM1gvotGe1ck+gHK+wApmBzOIiwJjg8FusFfgCA//hG5xjgNyOctqs/sLdZRY+Di9usZrB85N4hSPn3oAsd8qUBFxiLmeias40ynPt5fG12WKRnsaSzqNPEYry+rbb5m+GfSrobfxHWu4YtTFW9MMAAAAAElFTkSuQmCC",
                'form_url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-post-creator-poc-form',
                'url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-post-creator-poc-execute',
                'supported_formats': ['json', 'csv_zip'],
                'required_fields': [{"any_tag": ["sfdc_lead_id"]}],
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
            },
            {
                'name': 'salesforce-question-creator-poc',
                'label': 'Question',
                'supported_action_types': ['cell'],
                "icon_data_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABC0lEQVQ4jaXTL0vDURjF8c/zQ0RETCJG2RbE4GsYJjGbDT+LwVdgFLOYBfcCjGI2GUxiMI2tGERERERERHwMczD/4rYDF275nuce7nkiM8MQKoaBYaR7if3WCFERWSGauJQIE+RLlrWnnwwiMyMa7VFsYQPjeEQDk1jEFXZwiFE8Z1l97TVYko7En5HucYIpNGXu5lrtvGuwjc0+41+j3p141ycMM1gvotGe1ck+gHK+wApmBzOIiwJjg8FusFfgCA//hG5xjgNyOctqs/sLdZRY+Di9usZrB85N4hSPn3oAsd8qUBFxiLmeias40ynPt5fG12WKRnsaSzqNPEYry+rbb5m+GfSrobfxHWu4YtTFW9MMAAAAAElFTkSuQmCC",
                'form_url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-question-creator-poc-form',
                'url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-question-creator-poc-execute',
                'supported_formats': ['json', 'csv_zip'],
                'required_fields': [{"any_tag": ["sfdc_lead_id"]}],
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
            },
            {
                'name': 'salesforce-poll-creator-poc',
                'label': 'Poll',
                'supported_action_types': ['cell'],
                "icon_data_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABC0lEQVQ4jaXTL0vDURjF8c/zQ0RETCJG2RbE4GsYJjGbDT+LwVdgFLOYBfcCjGI2GUxiMI2tGERERERERHwMczD/4rYDF275nuce7nkiM8MQKoaBYaR7if3WCFERWSGauJQIE+RLlrWnnwwiMyMa7VFsYQPjeEQDk1jEFXZwiFE8Z1l97TVYko7En5HucYIpNGXu5lrtvGuwjc0+41+j3p141ycMM1gvotGe1ck+gHK+wApmBzOIiwJjg8FusFfgCA//hG5xjgNyOctqs/sLdZRY+Di9usZrB85N4hSPn3oAsd8qUBFxiLmeias40ynPt5fG12WKRnsaSzqNPEYry+rbb5m+GfSrobfxHWu4YtTFW9MMAAAAAElFTkSuQmCC",
                'form_url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-poll-creator-poc-form',
                'url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-poll-creator-poc-execute',
                'supported_formats': ['json', 'csv_zip'],
                'required_fields': [{"any_tag": ["sfdc_lead_id"]}],
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
            },
            {
                'name': 'salesforce-task-creator-poc',
                'label': 'New Task',
                'supported_action_types': ['cell'],
                "icon_data_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABC0lEQVQ4jaXTL0vDURjF8c/zQ0RETCJG2RbE4GsYJjGbDT+LwVdgFLOYBfcCjGI2GUxiMI2tGERERERERHwMczD/4rYDF275nuce7nkiM8MQKoaBYaR7if3WCFERWSGauJQIE+RLlrWnnwwiMyMa7VFsYQPjeEQDk1jEFXZwiFE8Z1l97TVYko7En5HucYIpNGXu5lrtvGuwjc0+41+j3p141ycMM1gvotGe1ck+gHK+wApmBzOIiwJjg8FusFfgCA//hG5xjgNyOctqs/sLdZRY+Di9usZrB85N4hSPn3oAsd8qUBFxiLmeias40ynPt5fG12WKRnsaSzqNPEYry+rbb5m+GfSrobfxHWu4YtTFW9MMAAAAAElFTkSuQmCC",
                'form_url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-task-creator-poc-form',
                'url': 'https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-task-creator-poc-execute',
                'supported_formats': ['json', 'csv_zip'],
                'required_fields': [{"any_tag": ["sfdc_lead_id"]}],
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


def salesforce_action_oauth(request):
    """Return form endpoint data for action"""
    code = request.args.get('code')
    encrypted_state = request.args.get('state')
    state_url = utils.decode_state(encrypted_state)

    client_id = os.environ.get('SALESFORCE_CLIENT_ID')
    client_secret = os.environ.get('SALESFORCE_CLIENT_SECRET')
    # redirect_uri = os.environ.get('SALESFORCE_REDIRECT_URI', 'https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/token')
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": "https://asia-southeast1-joon-sandbox.cloudfunctions.net/salesforce-action-poc-oauth"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    url = "https://one-line--ofuat.sandbox.my.salesforce.com/services/oauth2/token"

    encoded_payload = urlencode(payload)

    response = requests.post(url, headers=headers, data=encoded_payload, timeout=10)
    print(f"response: {response.json()}")
    print(f"response.status_code: {response.status_code}")

    if response.status_code in [200, 201]:
        token = response.json()['access_token']
        utils.store_state(state_url, {'token': token})
        # return redirect(f"{BASE_DOMAIN}form")
        return Response(response="Salesforce Authorized Successfully", status=response.status_code, mimetype="application/json")
    else:
        return Response(response=response, status=response.status_code, mimetype="application/json")