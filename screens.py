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
from functions import *

def screen_0():
    st.title('Hi, I am Mr. Leap')
    st.subheader('I am your digital companion powered by Google Gemini, and I help you post your Real Estate Lead Ads in a matter of minutes')
    
    screen_0_cols = st.columns(2)
    with screen_0_cols[0]:
        gemini_api_key = st.text_input('Kindly input in your Gemini API key to get started', value=st.session_state.get('gemini_api_key', ''), type='password')
    
    if st.button("Let's get started"):
        if gemini_api_key:
            st.session_state['gemini_api_key'] = gemini_api_key
            with st.spinner('Configuring the api_key'):
                genai.configure(api_key=st.session_state['gemini_api_key'])
            st.session_state['screen'] = 'screen_1'
            st.experimental_rerun()

        else:
            st.alert('Please input an API key to proceed!')

def screen_1():

    if st.button('Back'):
        st.session_state['screen'] = 'screen_0'
        st.experimental_rerun()

    screen_1_cols = st.columns([0.5, 1, 0.5])

    with screen_1_cols[1]:
        if 'progress' not in st.session_state:
            st.session_state['progress'] = 'Fill Form'
        
        st.title("Let's start!")
        url_input = st.text_input('You can optionally enter your landing page URL to fasten the process!', value=st.session_state.get('url', ''))

        if st.button("Let's Go!"):
            # if not url_input:
            #     st.warning("Please paste the URL.")
            # else:
            st.session_state['url'] = url_input
            # st.session_state['url']
            
            with st.spinner('Parsing URL and structuring data...'):
                if st.session_state['url'] != '':
                    soup = fetch_and_parse(url_input)
                    if soup:
                        text_content = extract_all_text(soup)
                        st.session_state['json_data'] = process_data(text_content)
                    
                    else:
                        st.session_state['json_data'] = {'Name': '', 'Address': '', 'Starting Price': '', 'Size': '', 'Key Highlights': ''}
                
                else:
                        st.session_state['json_data'] = {'Name': '', 'Address': '', 'Starting Price': '', 'Size': '', 'Key Highlights': ''}


        if 'json_data' in st.session_state and st.session_state['json_data']:
            json_data = st.session_state['json_data']
            with st.form(key='details_form'):
                form_data = {}
                for key, value in json_data.items():
                    if key == 'Key Highlights':
                        form_data[key] = st.text_area(key, value, height=100)
                    else:
                        form_data[key] = st.text_input(key, value)
                
                creative_option = st.radio(
                "Do you have your own creative?",
                ('Yes, I\'ll upload my own creative', 'No, I want you to design a creative for me'),
                index=0
                )

                # uploaded_files = st.file_uploader("Upload Property Images", type=['jpg', 'png'], accept_multiple_files=True)
                # if uploaded_files:
                #     st.image([file.getvalue() for file in uploaded_files], width=150, caption=["Uploaded Image"] * len(uploaded_files))
                
                submitted = st.form_submit_button("Proceed")
                
                if submitted:
                    if not all(form_data.values() or not creative_option):
                        st.error("Please fill in all fields to proceed.")
                    else:
                        st.session_state.update({
                            'form_data': form_data,
                            'creative_option': creative_option,
                        })
                        st.session_state['progress'] = 'Upload_image'
                        # st.success("Data saved! Proceed with next steps.")

            if st.session_state['progress'] == 'Upload_image':

                if st.session_state['creative_option'] == 'Yes, I\'ll upload my own creative':

                    uploaded_files = st.file_uploader("Please upload a creative you want to publish", type=['jpg', 'png'], accept_multiple_files=False)
                    
                    if uploaded_files:
                        st.session_state.update({
                            'uploaded_files': uploaded_files.getvalue(),
                        })
                        # st.image([file.getvalue() for file in uploaded_files], width=150, caption=["Uploaded Image"] * len(uploaded_files))
                    if 'uploaded_files' in st.session_state:
                        st.image(st.session_state['uploaded_files'], width=150)
                else:
                    uploaded_files = st.file_uploader("Please upload a good quality picture of your property and we'll create a creative for you!", type=['jpg', 'png'], accept_multiple_files=False)
                    if uploaded_files:
                        st.session_state.update({
                            'uploaded_files': uploaded_files.getvalue(),
                        })
                        # st.image([file.getvalue() for file in uploaded_files], width=150, caption=["Uploaded Image"] * len(uploaded_files))
                    if 'uploaded_files' in st.session_state:
                        st.image(st.session_state['uploaded_files'], width=150)
                        
                if st.button('Let\'s go'):
                    if not st.session_state['uploaded_files']:
                        st.error("Please upload the images to proceed.")

                    else:
                        st.session_state.update({
                            'uploaded_image': BytesIO(st.session_state['uploaded_files'])
                        })
                        
                        with st.spinner("Initializing your creatives"):

                            creative_copy_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                                        generation_config=generation_config,
                                                        system_instruction=creative_copy_instructions,
                                                        safety_settings=safety_settings)
                            
                            creative_copies = creative_copy_model.generate_content(json.dumps(st.session_state['form_data']))
                            st.session_state.update({
                                'creative_copies' : json.loads(creative_copies.text) 
                                })

                            img = Image.open(st.session_state.uploaded_image)

                            # Set up the generative model
                            color_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                                        generation_config=generation_config,
                                                        system_instruction=creative_colors_intructions,
                                                        safety_settings=safety_settings)
                            

                            # Generate content based on the uploaded image
                            recommended_colors_response = color_model.generate_content(img)
                            st.session_state.update({
                                'recommended_colors' : json.loads(recommended_colors_response.text)
                                })
                            
                        with st.spinner("Creating Ad Copies"):
                            ad_copy_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                                        generation_config=generation_config,
                                                        system_instruction=ad_copy_instruction,
                                                        safety_settings=safety_settings)
                            

                            # Generate content based on the uploaded image
                            ad_copy_response = ad_copy_model.generate_content(json.dumps(st.session_state['json_data']))
                            st.session_state.update({
                                'ad_copies' : json.loads(ad_copy_response.text)
                                })
                        
                        st.session_state['screen'] = 'screen_2'
                        st.experimental_rerun()

def screen_2():

    # print(st.session_state.creatives)

    #uploaded_image = BytesIO(st.session_state['uploaded_files'])

    if 'creatives' not in st.session_state:
        st.session_state['creatives'] = []

    if st.button('Back to screen 1', key = 'screen_2_back'):
        # st.session_state['creatives'] = []
        st.session_state['screen'] = 'screen_1'
        st.experimental_rerun()

    st.title("Creative Dashboard")

    image_1 = editor_and_layout_ad_1(st.session_state.uploaded_image, st.session_state.recommended_colors['light'], st.session_state.recommended_colors['dark'], st.session_state.creative_copies)
    if st.button('Add Image 1'):
        st.session_state.creatives.append(image_1)
    st.write('---')
    image_2 = editor_and_layout_ad_2(st.session_state.uploaded_image, st.session_state.recommended_colors['light'], st.session_state.recommended_colors['dark'], st.session_state.creative_copies)
    if st.button('Add Image 2'):
        st.session_state.creatives.append(image_2)
    st.write('---')
    image_3 = editor_and_layout_ad_3(st.session_state.uploaded_image, st.session_state.recommended_colors['light'], st.session_state.recommended_colors['dark'], st.session_state.creative_copies)
    if st.button('Add Image 3'):
        st.session_state.creatives.append(image_3)
    st.write('---')

    thumbnail_columns = st.columns(6)

    if len(st.session_state.creatives) > 3:
        
        for idx, img in enumerate(st.session_state.creatives[-3:]):
            with thumbnail_columns[idx]:
                st.image(img[0], caption=f'Image {idx}')

    else:
        for idx, img in enumerate(st.session_state.creatives):
            with thumbnail_columns[idx]:
                st.image(img[0], caption=f'Image {idx}')

    if st.button("Let's move on!"):
        if len(st.session_state.creatives) == 0:
            st.error("Please add atleast one of the creatives from above to proceed")
        else:
            st.session_state['screen'] = 'screen_3'
            st.experimental_rerun()

def screen_3():
    if st.button('Back to screen 2'):
        st.session_state['screen'] = 'screen_2'
        st.experimental_rerun()

    # st.write(st.session_state)

    st.title("Content Cards")

    copy_cols = st.columns(3)

    # Card 1: Primary Descriptions
    with copy_cols[0]:
        st.subheader("Primary Descriptions")
        st.session_state.ad_copies['Primary Descriptions'] = st.text_area("Edit Text:", value=st.session_state.ad_copies['Primary Descriptions'], height=200)

    # Card 2: Headline
    with copy_cols[1]:
        st.subheader("Headline")
        st.session_state.ad_copies['Headline'] = st.text_area("Edit Text:", value=st.session_state.ad_copies['Headline'], height=200)

    # Card 3: Link Description
    with copy_cols[2]:
        st.subheader("Link Description")
        st.session_state.ad_copies['Link Description'] = st.text_area("Edit Text:", value=st.session_state.ad_copies['Link Description'], height=200)

    # Submit button to save changes
    if st.button("Save Changes"):
        st.session_state.screen = 'screen_4'
        st.experimental_rerun()

import streamlit as st
from docx import Document
import os

import streamlit as st

def screen_4():
    if st.button('Back to screen 3'):
        st.session_state['screen'] = 'screen_3'
        st.experimental_rerun()

    st.title("Let's post your FB Leads Ad Now")

    access_token = st.text_input("You'll have to share your access token with us", type="password")

    if st.button("Done"):
        if access_token:
            st.session_state.update({
                'access_token': access_token
            })
            init_facebook(st.session_state['access_token'])

            with st.spinner("Processing the access token"):
                st.session_state.user_profile = get_user_profile(st.session_state['access_token'])
                st.session_state['ad_accounts'] = get_ad_accounts()
                st.session_state['pages'] = get_pages(st.session_state.access_token)
            
            st.session_state['screen'] = 'screen_5'
            st.experimental_rerun()

        else:
            st.error("Please enter your Facebook Access Token to proceed.")

    # Instructions Expander
    with st.expander("Instructions", expanded=False):
        st.markdown(instructions_manual, unsafe_allow_html=True)


def screen_5():
    if st.button('Back to screen 4'):
        st.session_state['screen'] = 'screen_4'
        st.experimental_rerun()

    # if 'user_profile' not in st.session_state:
    #     st.session_state.user_profile = get_user_profile(st.session_state['access_token'])

    if st.session_state['user_profile']:
        st.title(f"Welcome, {st.session_state['user_profile'].get('name')}!")

    # if 'ad_accounts' not in st.session_state and 'pages' not in st.session_state:
        # st.session_state['ad_accounts'] = get_ad_accounts()
        # st.session_state['pages'] = get_pages(st.session_state.access_token)

    if 'ad_accounts' in st.session_state and 'pages' in st.session_state: 
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Pages")
            selected_page_id = st.selectbox("Select a Page", list(st.session_state['pages'].keys()), format_func=lambda x: st.session_state['pages'][x])
        with col2:
            st.subheader("Ad Accounts")
            selected_ad_account_id = st.selectbox("Select an Ad Account", list(st.session_state['ad_accounts'].keys()), format_func=lambda x: st.session_state['ad_accounts'][x])
        
        screen_5_cols = st.columns(2)
        with screen_5_cols[0]:
            budget = st.number_input("What budget do you want to deploy on the campaign? (In INR)", min_value=2000, value=10000, step=2000, format="%d")

        if st.button("Let's Launch The Campaign Now!"):
            st.session_state.screen = 'screen_5'
            st.session_state['selected_page_id'] = selected_page_id
            st.session_state['selected_page_name'] = st.session_state['pages'][selected_page_id]
            st.session_state['selected_ad_account_id'] = selected_ad_account_id
            st.session_state['selected_ad_account_name'] = st.session_state['ad_accounts'][selected_ad_account_id]
            st.session_state['campaign_budget'] = budget

            st.session_state['screen'] = 'screen_6'

            st.experimental_rerun()

def screen_6():
    st.title('Campaign creation is on!')
    st.subheader('Check your ads manager in 2 minutes')

    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    init_facebook(st.session_state['access_token'])
    
    with st.spinner("Creating Campaign"):
        st.session_state['campaign_result'] = create_facebook_campaign(st.session_state['selected_ad_account_id'],
                                                                       st.session_state.json_data['Name'] + '_' + 'Campaign' + '_' + current_time,
                                                                       st.session_state['campaign_budget'])
        
    if st.session_state['campaign_result']['success']:
        st.success(f"Campaign Created Successfully: {st.session_state.json_data['Name'] + '_' + 'Campaign' + '_' + current_time}!")
    
    with st.spinner("Creating Adset"):
        audience_code_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                        generation_config=non_json_generation_config,
                                        system_instruction=audience_code_instruction,
                                        safety_settings=safety_settings)
        
        audience_code_response = audience_code_model.generate_content(json.dumps(st.session_state.json_data))

        st.session_state.update({
            'audience_code' : audience_code_response.text
            })
        
        geo_loc_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                                    generation_config=non_json_generation_config,
                                                    system_instruction=geo_loc_instruction,
                                                    safety_settings=safety_settings)
        
        # Generate content based on the uploaded image
        geo_loc_response = geo_loc_model.generate_content(st.session_state.json_data['Address'])
        st.session_state.update({
            'geo_loc' : geo_loc_response.text
            })

        if 'targeting_spec_table' not in st.session_state and 'geo_keys_table' not in st.session_state:
            st.session_state['targeting_spec_table'] = pd.read_excel('saved_aud_wo_geo.xlsx')
            st.session_state['geo_keys_table'] = pd.read_excel('city_keys.xlsx')
        
        st.session_state['targeting_wo_geo'] = get_targeting(st.session_state.targeting_spec_table, st.session_state.audience_code)
        # print(targeting_wo_geo)

        st.session_state['geo_key'], st.session_state['geo_radius'] = get_geo_key(st.session_state.geo_keys_table, st.session_state.geo_loc)
        # print(key)

        # radius = get_geo_key(geo_keys_table, geo_loc)[1]
        # print(radius)

        # st.write(st.session_state.targeting)
        # st.write(st.session_state.geo_key)
        
        targeting = st.session_state.targeting_wo_geo
        targeting["geo_locations"]["cities"].append({"key": st.session_state['geo_key'].strip(), "radius":st.session_state['geo_radius'].strip(), "distance_unit": "kilometer"})
        st.session_state['targeting'] = targeting

        print(st.session_state['targeting'])

        start_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        end_time = start_time + datetime.timedelta(days=15)

        st.session_state['adset_result'] = create_facebook_adset(st.session_state['selected_ad_account_id'],
                                                                    st.session_state.json_data['Name']+'_'+'Adset'+current_time,
                                                                    st.session_state.campaign_result['campaign_id'], st.session_state['targeting'],
                                                                    st.session_state['selected_page_id'], start_time, end_time)
        
    
    # st.write(st.session_state['adset_result'])
    if st.session_state['adset_result']['success']:
        st.success(f"Adset Created Successfully! {st.session_state.json_data['Name'] + '_' + 'Adset' + '_' + current_time}")


    with st.spinner("Preparing assets for the Ad"):

        st.session_state['image_hashes'] = []
        if len(st.session_state.creatives) > 3:
            for creative in st.session_state.creatives[-3:]:
                adimage = create_facebook_adimage(st.session_state.access_token, st.session_state.selected_ad_account_id, creative[1])
                st.session_state.image_hashes.append(adimage['data']['images']['bytes']['hash'].strip())
                #st.write(result['data']['images']['bytes']['hash'])
        
        else:
            for creative in st.session_state.creatives:
                adimage = create_facebook_adimage(st.session_state.access_token, st.session_state.selected_ad_account_id, creative[1])
                st.session_state.image_hashes.append(adimage['data']['images']['bytes']['hash'])

        st.session_state['leadform'] = create_facebook_lead_form(st.session_state.access_token, st.session_state.selected_page_id,
                                            st.session_state.json_data['Name']+'_'+'leadform' + current_time, st.session_state.json_data['Name'], [st.session_state.ad_copies['Primary Descriptions']], 'PARAGRAPH_STYLE', st.session_state['url'])
        # st.write(st.session_state.ad_copies['Primary Descriptions'])
        # st.write(st.session_state['leadform'])
        st.session_state['leadform_id'] = st.session_state['leadform']['form_id']

    # st.write(st.session_state['image_hashes'])

    # st.session_state['leadform_id']

    if 'images_hashes' in st.session_state and 'leadform_id' in st.session_state:
        st.success(f"Assets prepared Successfully!")

    with st.spinner('Final Touches'):
        st.session_state['adcreative_ids'] = []
        st.session_state['ad_ids'] = []
        for i, image_hash in enumerate(st.session_state['image_hashes']):
            # st.write(image_hash)
            creative = create_facebook_adcreative(st.session_state.selected_ad_account_id, 
                                                  st.session_state.ad_copies['Primary Descriptions'],
                                                  st.session_state.ad_copies['Headline'],
                                                  st.session_state.ad_copies['Link Description'],
                                                  st.session_state.ad_copies['Link Description'] + '__',
                                                  image_hash,
                                                  st.session_state.selected_page_id,
                                                  st.session_state['leadform_id'],
                                                  st.session_state.json_data['Name'] + '_AdCreative_' + str(i))
            # st.write(creative)
            st.session_state['adcreative_ids'].append(creative['ad_creative_id'])
            ad = create_facebook_ad(st.session_state.selected_ad_account_id,
                                    st.session_state.json_data['Name'] + '_Ad_' + str(i), 
                                    st.session_state['adset_result']['adset_id'],
                                    creative['ad_creative_id'])
            
            # st.write(ad)
            
            st.session_state['ad_ids'].append(ad['ad_id'])

        
    st.success('Congrats! Your Ad Campaign has been posted')

        
    # st.write(len(st.session_state.creatives))
    # st.write(st.session_state.creatives)
