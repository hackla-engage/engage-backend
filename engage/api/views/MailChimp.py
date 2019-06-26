from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json
from os import getenv

REGION = getenv('MAILCHIMP_REGION')
KEY = getenv('MAILCHIMP_KEY')
USER = getenv('MAILCHIMP_USER')

def mailchimpCheckMemberRequest(email=None, user=None, key=None):
    """
    HTTP Method: GET
    MailChimp API request used to get the details of an existing user.
    """
    user = user
    key = key
    url = f'https://{REGION}.api.mailchimp.com/3.0/search-members?query={email}'

    r = requests.get(url, auth=(user, key))

    return r

def mailchimpUpdRequest(payload=None, user=None, key=None, member_id=None):
    """
    HTTP Method: PATCH
    MailChimp API request used to update the status of existing users.
    """
    user = user
    key = key
    url = f'https://{REGION}.api.mailchimp.com/3.0/lists/6ca892a88b/members/{member_id}'

    r = requests.patch(url, auth=(user, key), data=payload)

    return r


def mailchimpSubRequest(payload=None, user=None, key=None):
    """
    HTTP Method: POST
    MailChimp API request used to subscribe new users.
    """
    user = user
    key = key
    url = f'https://{REGION}.api.mailchimp.com/3.0/lists/6ca892a88b/members/'

    r = requests.post(url, auth=(user, key), data=payload)

    return r


@api_view(['POST'])
def mailChimpSub(request):
    user = USER
    key = KEY

    payload = request.data
    payload = json.dumps(payload)
    response = mailchimpSubRequest(payload=payload, user=user, key=key)

    email = json.loads(payload)['email_address']
    mc_response = json.loads(response.text)

    if response.status_code == 200:
        data = "Congratulation. {} has successfuly been subscribed".format(email)
        return Response(data=data, status=200)

    elif response.status_code == 400:
        # load the MailChimp error response
        mc_response = json.loads(response.text)

        if mc_response['title'] and mc_response['title'] == 'Member Exists':
            # check if member has unscribed and wants to resuscribe
            member_request = mailchimpCheckMemberRequest(email=email, user=user, key=key)
            member_request_json_resp = json.loads(member_request.text)
            status = member_request_json_resp['exact_matches']['members'][0]['status'] # Get member subscribtion status
            
            if status == 'unsubscribed':
                member_id = member_request_json_resp['exact_matches']['members'][0]['id']
                payload = {
                    'email_address': f'{email}',
                    'status': 'subscribed'
                }
                payload = json.dumps(payload)

                # Run a patch method to update member subscrition status
                response = mailchimpUpdRequest(payload=payload, user=user, key=key,
                                            member_id=member_id)

                if response.status_code == 200:
                    data = f'{email} has successfuly been resuscribed'
                    return Response(data=data, status=200)

                else:
                    data = f'Oops! Something wrong happened. We could not identify the issue, contact us at engage@engage.town'
                    return Response(data=data, status=401)
                
            else:
                data =  "{} member is already subscribed.".format(email)
                return Response(data=data, status=400)

        # Catch all error for un identified error response
        else:
            data = f'Oops! Something wrong happened. We could not identify the issue, contact us at engage@engage.town'
            return Response(data=data, status=401)

    # Catch all error for un identified error response
    else:
        data = f'Oops! Something wrong happened. We could not identify the issue, contact us at engage@engage.town'
        return Response(data=data, status=401)