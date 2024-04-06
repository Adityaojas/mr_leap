import streamlit as st
import google.generativeai as genai
from config import *
import json



if 'current_screen' not in st.session_state:
    st.session_state['current_screen'] = 'form_screen'

# Function to process the URL
def process_url(url):
    genai.configure(api_key="AIzaSyBYnwPKTiggqKSFR7xKeUJ2xgBSxuaQh_w")

    model = genai.GenerativeModel(model_name=model_name,
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    convo = model.start_chat(history=history)
    convo.send_message(user_input.format(url))
    print(convo.last.text)

    return json.loads(convo.last.text.replace('`','').replace('JSON', '').replace('json', ''))

def display_form_screen():
    st.set_page_config(layout="wide")

    default_url = st.session_state.get('url_data', {}).get('url', '')
    url = st.sidebar.text_input('Kindly copy and paste your URL in the space provided below', value=default_url)
    
    if st.sidebar.button('Submit URL'):
        st.session_state['url_data'] = process_url(url)
        st.session_state['url_data']['url'] = url
        # st.session_state['amenity_index'] = 0  # Reset amenity index each time new URL is submitted

    if 'url_data' in st.session_state:
        with st.form(key='data_form'):
            # Editable fields for dictionary values
            data = st.session_state['url_data']

            name = data.get('Name', '')
            address = data.get('Address', '')
            type_ = data.get('Type', 'Residential')  # Example default
            subtype = data.get('Subtype', 'Flat')  # Example default
            amenities = data.get('Amenities', '')
            price = data.get('Price Range', '')
            size = data.get('Sizes', '')
            status = data.get('Status', 'Ready to Move')

            print(data)

            st.session_state['url_data']['name'] = st.text_input('Name', value=name, key='name')
            st.session_state['url_data']['address'] = st.text_input('Address', value=address, key='address')

            type_col, subtype_col = st.columns(2)
            
            types = ['Residential', 'Commercial']
            subtypes = ['Flat', 'House/Villa', 'Plot', 'Office Space', 'Shop/Showroom', 'Commercial Land']

            with type_col:
                st.session_state['url_data']['type'] = st.selectbox('Type', types, index=types.index(type_), key='type')

            with subtype_col:
                st.session_state['url_data']['subtype'] = st.selectbox('Sub Type', subtypes, index=subtypes.index(subtype), key='subtype')
            
            st.session_state['url_data']['amenities'] = st.text_input('Amenities', value=amenities, key='amenities')
            #st.session_state['url_data']['amenities'] = ', '.join(amenities)

            price_col, size_col = st.columns(2)
            with price_col:
                st.session_state['url_data']['price'] = st.text_input('Price', value=price, key='price')
            
            with size_col:
                st.session_state['url_data']['size'] = st.text_input('Sizes', value=size, key='size')

            status_col, _ = st.columns(2)
            statuses = ['Under Construction', 'Ready to Move']

            with status_col:
                st.session_state['url_data']['status'] = st.selectbox('Status', statuses, index=statuses.index(status), key='status')

            submitted = st.form_submit_button('Confirm')

            if submitted:
                # Check if any required field is empty
                required_fields = [st.session_state['url_data'].get('name'), st.session_state['url_data'].get('address'), st.session_state['url_data'].get('type'), st.session_state['url_data'].get('subtype'), st.session_state['url_data'].get('amenities'), st.session_state['url_data'].get('price'), st.session_state['url_data'].get('size'), st.session_state['url_data'].get('status')]

                # Add a check to see if any of the fields are empty
                if any(field == None for field in required_fields):
                    st.warning('Please fill in all the fields to proceed!')
            
                else:
                    # Your existing code to show success and JSON data
                    # st.success('Data confirmed!')
                    st.session_state['current_screen'] = 'upload_screen'
            

def display_upload_screen():
    st.title("Upload a Creative for the Project")
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg', 'gif'])
    
    if uploaded_file is not None:
        # Save the uploaded file in session state
        st.session_state['uploaded_creative'] = uploaded_file
    
    col1, col2 = st.columns(2)
    
    if col1.button("Back"):
        # Go back to the form screen, maintaining the current state 50000000
        st.session_state['current_screen'] = 'form_screen'
    
    if col2.button("Submit"):
        # Proceed with saving the image and other data
        st.success("Creative uploaded successfully!")
        # Add any actions you want to take after the image has been uploaded

# Screen management
if st.session_state['current_screen'] == 'form_screen':
    display_form_screen()
elif st.session_state['current_screen'] == 'upload_screen':
    display_upload_screen()