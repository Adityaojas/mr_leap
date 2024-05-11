from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.user import User as AdUser
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.exceptions import FacebookRequestError
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad



import pandas as pd
import streamlit as st
import requests
import json


def init_facebook(access_token):
    FacebookAdsApi.init(access_token=access_token, api_version='v19.0')

def get_user_profile(access_token):
    """Fetch the user's profile information to get the name."""
    try:
        url = f"https://graph.facebook.com/v19.0/me?fields=name&access_token={access_token}"
        response = requests.get(url)
        return response.json()  # Returns a dictionary with user name and id
    except Exception as e:
        st.error(f"Error fetching user profile: {e}")
        return {}
    

def get_ad_accounts():
    try:
        me = AdUser(fbid='me')
        ad_accounts = me.get_ad_accounts(fields=['id', 'name'])
        return {acc['id']: acc['name'] for acc in ad_accounts}
    except Exception as e:
        st.error(f"Error fetching ad accounts: {e}")
        return {}
    

def get_pages(access_token):
    try:
        url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={access_token}"
        response = requests.get(url)
        pages = response.json()
        return {page['id']: page['name'] for page in pages['data']}
    except Exception as e:
        st.error(f"Error fetching pages: {e}")
        return {}
    
def get_targeting(df, code):
    targeting_info = df[df['Code'] == str(code.replace("\\", "").strip())]['targeting']
    if not targeting_info.empty:
        return json.loads(targeting_info.iloc[0])
    else:
        return df[df['Code'] == 'Res_L_LC']['targeting'].iloc[0]

def get_geo_key(df, geo):
    key = df[df['search_query'] == geo.lower()]['key']
    radius = df[df['search_query'] == geo.lower()]['radius']
    if not key.empty:
        return [key.iloc[0], radius.iloc[0]]
    else:
        return ["1026297", "20"]
    
    
def create_facebook_campaign(ad_account_id, campaign_name, budget):
    try:
        ad_account = AdAccount(ad_account_id)
        params = {
            'name': campaign_name,
            'status': 'PAUSED',
            'objective': 'OUTCOME_LEADS',
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'buying_type': 'AUCTION',
            'lifetime_budget': str(int(budget) * 100),  # Assuming budget input is in whole numbers, converting to smallest currency unit.
            'pacing_type': ['day_parting'],
            'smart_promotion_type': 'GUIDED_CREATION',
            'special_ad_categories': [],
            # 'special_ad_category': 'NONE'
        }
        campaign = ad_account.create_campaign(params=params)
        return {'success': True, 'campaign_id': campaign['id']}
    
    except FacebookRequestError as e:
        return {'success': False, 'error': str(e)}
    
def create_facebook_adset(ad_account_id, name, campaign_id, targeting, page_id, start_time, end_time):
    try:
        ad_account = AdAccount(ad_account_id)
        params = {
            'name': name,
            'campaign_id': campaign_id,
            'status': 'PAUSED',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': 'LEAD_GENERATION',
            'targeting': targeting,
            'promoted_object': {'page_id': page_id},
            'destination_type': 'ON_AD',
            'adset_schedule': [
                {'days': [0, 1, 2, 3, 4, 5, 6], 'start_minute': 420, 'end_minute': 1440, 'timezone_type': 'USER'},
                {'days': [0, 1, 2, 3, 4, 5, 6], 'start_minute': 0, 'end_minute': 60, 'timezone_type': 'USER'}
            ]
        }
        adset = ad_account.create_ad_set(params=params)
        return {'success': True, 'adset_id': adset['id']}
    except FacebookRequestError as e:
        return {'success': False, 'error': str(e)}
    

def create_facebook_adimage(access_token, ad_account_id, base64_image):
    url = f"https://graph.facebook.com/v19.0/{ad_account_id}/adimages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "bytes": base64_image
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return {'success': True, 'data': response.json()}
    else:
        return {'success': False, 'error': response.text}
    

def create_facebook_lead_form(access_token, page_id, form_name, title, content, style, url):
    url = f"https://graph.facebook.com/v19.0/{page_id}/leadgen_forms"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        'name': form_name,
        'privacy_policy': {
            'url': 'https://www.leapx.ai/privacy-policy',
            'link_text': 'Privacy Policy'
        },
        'question_page_custom_headline': 'Please answer the following questions',
        'questions': [
                        {
                            "key": "when_are_you_planning_to_purchase",
                            "label": "When are you planning to purchase?",
                            "options": [
                                {"key": "Immediately", "value": "Immediately"},
                                {"key": "<1Month", "value": "< 1 Month"},
                                {"key": "1-3 Months", "value": "1-3 Months"},
                                {"key": "just_collecting_information", "value": "Just collecting information"}
                            ],
                            "type": "CUSTOM"
                        },
                        {
                            "key": "your_whatsapp_number",
                            "label": "What's your WhatsApp Number",
                            "type": "CUSTOM"
                        },
                        {
                            "key": "email",
                            "type": "EMAIL"
                        },
                        {
                            "key": "full_name",
                            "type": "FULL_NAME"
                        },
                        {
                            "key": "phone_number",
                            "type": "PHONE"
                        }
                    ]
                    ,
        'context_card': {
            'title': title,
            'content': content,
            'style': style
        },
        'follow_up_action_url': url
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return {'success': True, 'form_id': response.json()['id']}
    else:
        return {'success': False, 'error': response.json().get('error', {}).get('message', 'Unknown error')}


def create_facebook_adcreative(ad_account_id, body_text, description_text, title_1, title_2, image_hash, page_id, lead_form_id, name):
    try:
        ad_account = AdAccount(ad_account_id)
        params = {
            'name': name,
            'object_story_spec': {
                'page_id': page_id,
                'link_data': {
                    'link': 'http://fb.me/',
                    'image_hash': image_hash,
                    'attachment_style': 'link',
                    'call_to_action': {
                        'type': 'LEARN_MORE',
                        'value': {
                            'lead_gen_form_id': lead_form_id
                        }
                    }
                }
            },
            'asset_feed_spec': {
                'bodies': [{'text': body_text}],
                'descriptions': [{'text': description_text}],
                'titles': [{'text': title_1}, {'text': title_2}],
                'optimization_type': 'DEGREES_OF_FREEDOM'
            },
            # 'image_hash': image_hash,
            'degrees_of_freedom_spec': {
                'creative_features_spec': {
                    'advantage_plus_creative': {'enroll_status': 'OPT_OUT'},
                    'cv_transformation': {'enroll_status': 'OPT_OUT'},
                    'image_enhancement': {'enroll_status': 'OPT_OUT'},
                    'image_templates': {'enroll_status': 'OPT_OUT'},
                    'image_touchups': {'enroll_status': 'OPT_OUT'},
                    'image_uncrop': {'enroll_status': 'OPT_OUT'},
                    'inline_comment': {'enroll_status': 'OPT_OUT'},
                    'standard_enhancements': {'enroll_status': 'OPT_IN'},
                    'text_optimizations': {'enroll_status': 'OPT_IN'}
                }
            }
        }
        ad_creative = ad_account.create_ad_creative(params=params)
        return {'success': True, 'ad_creative_id': ad_creative['id']}
    except FacebookRequestError as e:
        return {'success': False, 'error': str(e)}


def create_facebook_ad(ad_account_id, ad_name, adset_id, adcreative_id):
    try:
        ad_account = AdAccount(ad_account_id)
        params = {
            'name': ad_name,
            'adset_id': adset_id,
            'creative': {'creative_id': adcreative_id},
            'status': 'PAUSED'  # Start the ad as paused to avoid immediate billing and allow for review.
        }
        ad = ad_account.create_ad(params=params)
        return {'success': True, 'ad_id': ad['id']}
    except FacebookRequestError as e:
        return {'success': False, 'error': str(e)}