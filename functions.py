import streamlit as st
import requests
from requests.exceptions import RequestException, Timeout
import time
from bs4 import BeautifulSoup, Comment
import json
import google.generativeai as genai
from config import *
from creative_automation_module import *
from templates_and_editors import *
from io import BytesIO
import pandas as pd

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.exceptions import FacebookRequestError

from fb_modules import *
import datetime

# Assuming you have a function like this, here is a placeholder for process_data
def process_data(parsed_data):

    model = genai.GenerativeModel(model_name=model_name,
                                generation_config=generation_config,
                                system_instruction=system_instruction,
                                safety_settings=safety_settings,
                                )

    convo = model.start_chat()
    convo.send_message(parsed_data)

    return json.loads(convo.last.text)

def fetch_and_parse(url):
    """ Fetches the content from the URL and returns a BeautifulSoup object, with timeout and error handling. """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Timeout:
        # st.error("The request timed out. Please check the URL and try again.")
        pass
    except RequestException as e:
        st.write(f"There was an error fetching the page, request you to fill the following form manually")
    return None

def extract_all_text(soup):
    """ Extracts and returns all text from the soup object, if provided. """
    if not soup:
        return "Failed to parse the page."
    for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
        script_or_style.decompose()
    text = soup.get_text()
    return text.strip()
