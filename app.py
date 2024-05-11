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
from screens import *
import datetime


def main():

    if 'screen' in st.session_state:
        print(st.session_state['screen'])

    # if 'uploaded_files' in st.session_state:
    #     print(st.session_state['uploaded_files'])

    st.set_page_config(layout="wide")

    if 'screen' not in st.session_state:
        st.session_state['screen'] = 'screen_0'

    if st.session_state['screen'] == 'screen_0':
        screen_0()
    
    elif st.session_state['screen'] == 'screen_1':
        screen_1()

    elif st.session_state['screen'] == 'screen_2':
        screen_2()

    elif st.session_state['screen'] == 'screen_3':
        screen_3()

    elif st.session_state['screen'] == 'screen_4':
        screen_4()
    elif st.session_state['screen'] == 'screen_5':
        screen_5()

    elif st.session_state['screen'] == 'screen_6':
        screen_6()



if __name__ == "__main__":
    main()