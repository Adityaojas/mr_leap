import os

model_name="gemini-1.5-pro-latest"

generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
  "response_mime_type": "application/json"
}

non_json_generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 100
  }

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]

system_instruction = "You are a professional real estate marketer. People usually provide you with the  landing pages of their real estate projects and you simply parse through the website and identify the most important aspects of the property that can be used for marketing. First you summarize the property and then list down all the key highlights that may appeal to the audiences out there.\n\nNow I'll give you the data parsed from a real estate project landing page, and you have to give me a small json brief of the property that includes its name, address, starting price, and starting size of the property, and a small summary of the appealing highlights of the property that you can find in the parsed data. This summary should include everything you think can be included in the ad copy or creative. \n\nMake it a json dictionary format of the form:\n\n{\nName: <Name of the property/ project>,\nAddress: <Trim down the address to locality and city, not the full long address>,\nStarting Price <The price of the property, make sure that it is correct! For example: \"80 Lacs Onwards\", \"3 Cr Onwards\", etc.>,\nSize: <Return the starting size and add 'onwards' in the ned. For example: \"2 BHK Onwards\", \"600 sq ft. Onwards\" etc.,\nKey Highlights: <A summary of the key highlights of the property, in a comma-separated string. These are the highlights which may be included in the ad copy and creative>\n}\n\nInclude all the mentioned keys in the dictionary, and use only the keys which are mentioned. None other. If you do not find a specific field, then leave the value blank or empty space."

creative_colors_intructions = "You are a professional creative artist, and you design top-notch ad creatives for Facebook and Google marketing. You have opened up for Real Estate clients now. \n\nYou have several templates that you use to make creatives.\n\nBut the first job is to identify the colors from the assets you receive. Your job is to identify the colors that will resonate with the picture.\n\nSo your job here is to look at the image asset that I will show you and identify the best colors that would complement with that image.\n\nIdentify 7-8 dark colors, and 7-8 light colors that would add on to the aesthetic of the creative. Make sure that these colors are vibrant, aesthetic and appealing to the eye and the design. Only give the hex codes in a JSON format in the following structure:\n\n{\n\"dark\" :  [\"dark_hex_1\", \"dark_hex_2\", \"dark_hex_3\", \"dark_hex_4\", \"dark_hex_5\", ...],\n\"light\" :  [\"light_hex_1\", \"light_hex_2\", \"light_hex_3\", \"light_hex_4\", \"light_hex_5\", ...].\n}"

creative_copy_instructions = "You are a professional real estate marketer and copywriter. People provide you with some details of their property and you very appealingly extract quite a few copies out of that information.\n\nFor the purpose, You keep it in a maintained json dictionary format of the form:\n\n{Name : The name of the property,\n Hook : A hook line for the ad creative, mainly mentioning the sizes and price of the property (50-55 characters),\n Sub Description : A sub description, highlighting the property with some nice adjectives (20 - 25 characters)\n}\nYou extract only these 3 fields.\n\nI'll provide you with some details of a property and you'll give me the json dictionary, make sure to start and end with curly braces"

ad_copy_instruction = "You are a professional real estate marketer and copywriter. People provide you with some details of their property and you extract very fine and appealing copies for their marketing campaigns.\n\nFor the purpose, You keep it in a maintained json dictionary format of the form:\n\n{\nPrimary Descriptions : a very professional description of the property that detail the property's location, its amenities, the offers, and other important things in a captivating way. It can be around 300-400 characters. The art of writing the description is keeping it neat, including bullet points and seldomly using some professional emojis like tick marks. The starting few words of the description should be capturing and engaging enough that the user engages with the ad.\n\nHeadline: A captivating headilne specific to the property, within 30-40 charcters. The art is to keep it very clear, concise and UVP Focused. Do not include many jargons or fancy words. Keep it professional and engaging.\n\nLink Description: One liner link description for the users compelling them to fill the form. Not more than 50-70 characters. The art is to induce a sense of urgency and hurriedness among the readers and compel them to click the link in the ad.\n}\n\nI'll provide you with some details of a property and you'll give me the json dictionary. make sure to start and end with curly braces."

audience_code_instruction = "You are a savvy marketer. I will provide you some specific details about a property which can be residential, commercial, or plots. You are entrusted with finding baseline cohorts of audience for that property. I am sharing with you a table, which has 2 columns - description & audience targeting code. You need to first go through that and understand it.  You have to return the best-targeting audience code of the entire project based on the information of the property that I share. Remember to only output the code, nothing else.\n\nHere is the table:\nProperty description\tCode\n1 BHK Apartment, in Tier 1 location in the range of Rs. 0 - 0.5 Crores.\tRes_A_LC\n1 BHK Apartment, in Tier 1 location in the range of Rs. 0.51-1.0 Crores.\tRes_V_LC\n1 BHK Apartment, in Tier 1 location above Rs. 1 Crores.\tRes_L_LC\n1 BHK Apartment, in Tier 2 locations in the range of Rs. 0 - 0.5 Crores.\tRes_A_SC\n1 BHK Apartment, in Tier 2 location in the range of Rs. 0.51 - 1 Crores.\tRes_V_SC\n1 BHK Apartment, in Tier 2 above Rs. 1 Crores.\tRes_L_SC\n2 BHK and above in Tier 1 location in the range of - Rs. 0 - 1 Crores.\tRes_A_LC\n2 BHK and above in Tier 1 location in the range of - Rs. 1.001 - 2 Crores.\tRes_V_LC\n2 BHK and above in Tier 1 location in the range of - Rs. 2.001 Crore and above\tRes_L_LC\n2 BHK and above in Tier 2 location in the range of - Rs. 0 - 0.5 Crores.\tRes_A_SC\n2 BHK and above in Tier 2 location in the range of - Rs. 0.5 - 1 Crores.\tRes_V_SC\n2 BHK and above in Tier 2 location above 1 Crores.\tRes_L_SC\nLand/Plot in Tier 1 location in the range of - Rs. 0 - 1 Crores.\tPlot_A_LC\nLand/Plot in Tier 1 location in the range of - Rs. 1.0 Crores -3.0 Crores.\tPlot_V_LC\nLand/Plot in Tier 1 location in the range of - Rs. 3.0 Crores to 5.0 Crores.\tPlot_L_LC\nLand/Plot in Tier 2 location in the range of - Rs. 0 - 0.5 Crores.\tPlot_A_SC\nLand/Plot in Tier 2 location in the range of - Rs. 0.5 - 1.0 Crores.\tPlot_V_SC\nLand/Plot Tier 2 location above 1.0 Crores.\tPlot_L_SC\nShops, office space, SCO, commercial complex in Tier 1 location in the range of - Rs. 0 - 0.5 Crores.\tCom_A_LC\nShops, office space, SCO, commercial complex in Tier 1 location in the range of - Rs. 0.5 Crores - 1 Crores.\tCom_V_LC\nShops, office space, SCO, commercial complex in Tier 1 location above Rs 1 Crores.\tCom_L_LC\nShops, office space, SCO, commercial complex in Tier 2 location in the range of - Rs. 0 - 0.25 Crores.\tCom_A_SC\nShops, office space, SCO, commercial complex in Tier 2 location in the range of - Rs. 0.25 Crores - 0.5 Crores.\tCom_V_SC\nShops, office space, SCO, commercial complex in Tier 2 location above Rs 0.5 Crores.\tCom_L_SC"

geo_loc_instruction = "I am going to give you an address of a property, and you have to return me a single word answer of where the address belongs out of the following regions: Agra, Ahmedabad, Ajmer, Akola, Aligarh, Allahabad, Amravati, Amritsar, Asansol, Aurangabad, Bareilly, Belgaum, Bengaluru, Bhavnagar, Bhiwandi, Bhilai, Bhopal, Bhubaneswar, Bhuj, Bikaner, Chandigarh, Chennai, Chinchwad, Coimbatore, Cuttack, Dehradun, Delhi, Dhanbad, Dombivali, Durgapur, Erode, Faridabad, Firozabad, Gandhinagar, Ghaziabad, Gorakhpur, Guntur, Gurgaon, Guwahati, Gwalior, Howrah, Hubballi-Dharwad, Hyderabad, Indore, Jabalpur, Jaipur, Jalandhar, Jamnagar, Jamshedpur, Jhansi, Jodhpur, Kalyan, Kanpur, Kochi, Kolhapur, Kolkata, Kota, Lucknow, Ludhiana, Madurai, Malegaon, Mangalore, Meerut, Moradabad, Mumbai, Mysore, Nagpur, Nanded, Nashik, Navi Mumbai, Nellore, Noida, Patna, Pondicherry, Pune, Raipur, Rajkot, Ranchi, Rourkela, Salem, Saharanpur, Siliguri, Solapur, Srinagar, Surat, Thane, Thiruvananthapuram, Tiruchirappalli, Tirunelveli, Tiruppur, Ujjain, Ulhasnagar, Vadodara, Varanasi, Vasai-Virar, Vijayawada, Visakhapatnam, Warangal"

font_dir = 'C:/Windows/Fonts'  # Change this path based on your operating system

instructions_manual = """
        **Instructions Manual:**
        To prepare yourself to use Mr. Leap’s automation, you need to configure a few things at your end (This would hardly take 10 minutes, and is a one-time effort)
        
        ---
                    
        **Step 1: Create and Set Up Your Meta App**
        - **Create an App**: Begin by navigating to the Meta Developers portal. You will need to log in using your Facebook credentials. Once logged in, create a new app by selecting a relevant app type that suits your needs (e.g., Business).
        - **Configure Your App**: After creation, configure your app's settings. Enter the necessary details such as app name, contact email, and website URL.
        - **Switch to Live Mode**: Transition your app from development to live status to make it operational. This is crucial for your app to interact with Facebook on behalf of users.
                    
        ---
        
        
        **Step 2: Configure Graph API Access**
        - **Access Graph API Explorer**: Go to the Graph API Explorer tool. Here you will manage and test your app’s API requests.
        - **Generate Access Token**: In the Graph API Explorer, select your app from the top right dropdown menu. Then, click on the 'Generate Access Token' button.
        - **Set Permissions**: Specify permissions that your app requires to function. For comprehensive ads management, include the following permissions:
            - user_events
            - read_insights
            - pages_manage_cta
            - pages_manage_instant_articles
            - pages_show_list
            - ads_management
            - ads_read
            - business_management
            - leads_retrieval
            - page_events
            - pages_read_engagement
            - pages_manage_metadata
            - pages_read_user_content
            - pages_manage_ads
            - pages_manage_posts
            - pages_manage_engagement
        - **Save Your Token**: Securely save the access token generated. This token is necessary for making API requests on behalf of your app.

        ---
        
        **Step 3: Accept Terms of Service**
        - **Lead Ads Terms of Service**: Before you can publish ads or retrieve leads, visit [Meta Lead Ads Terms of Service](https://www.facebook.com/ads/leadgen/tos) and accept the terms for each of the pages you will use to publish ads.

        ---
                    
        **Step 4: Add a Billing Method**
        - **Configure Billing in Ad Account**: Navigate to your Facebook Ads Manager. Under the ‘Billing’ section, add and verify your billing method to enable ad spending. This is crucial as ads cannot run without a confirmed payment method.
        """