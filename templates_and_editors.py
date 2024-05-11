import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from creative_automation_module import *
import textwrap
import random
import io
from io import BytesIO
import base64
import os
from config import *

### TEMPLATES ###

def create_ad_template_1(uploaded_image, heading, description, upper_color, lower_color, heading_color, desc_color, font_path_1, font_path_2):
    # Colors as per the template
    dark_brown = "#CD853F"
    light_brown = "#F2E3CF"

    scale_factor = 1
    
    # Create a blank template image
    template_img = Image.new('RGB', (1024*scale_factor, 1024*scale_factor), upper_color)
    draw = ImageDraw.Draw(template_img)
    
    # Calculate the size of the two rectangles
    upper_rect_height = int(template_img.size[1] * 0.6)
    lower_rect_height = template_img.size[1] - upper_rect_height
    
    # Draw the light brown rectangle
    draw.rectangle([0, upper_rect_height, template_img.size[0], template_img.size[1]], fill=lower_color)

    margin_width = template_img.size[0] * 0.1
    frame_width = template_img.size[0] - 2 * margin_width
    frame_height = (upper_rect_height * 3/4 + lower_rect_height * 6/7 ) - (margin_width * 2) # Adjusted to account for 1/4th part in the bottom rectangle
    
    # Open the uploaded image and resize it if needed
    user_image = Image.open(uploaded_image).convert("RGBA")
    adjusted_image = adjust_and_crop_image(user_image, int(frame_width), int(frame_height))

    img_position_x = margin_width
    img_position_y = margin_width

    # user_image.thumbnail((template_img.size[0], upper_rect_height))
    
    # # Overlay the uploaded image onto the template
    # img_position = (int(template_img.size[1]*0.05), int(upper_rect_height * 0.1)) # Adjust vertical positioning as needed
    # template_img.paste(user_image, img_position, user_image)
    template_img.paste(adjusted_image, (int(img_position_x), int(img_position_y)), adjusted_image)

    # Draw the text onto the template
    draw = ImageDraw.Draw(template_img)
    
    # Load fonts
    heading_font_size = int(upper_rect_height * 0.1)  # Dynamically sized to the rectangle
    desc_font_size = int(lower_rect_height * 0.1)
    heading_font = ImageFont.truetype(font_path_1, heading_font_size)
    desc_font = ImageFont.truetype(font_path_2, desc_font_size)

    # Define maximum text width (for example, image width - 10% margin on each side)
    max_text_width = int(template_img.size[0]*0.8)
    # print(max_text_width)

    # Wrap the heading and description texts
    wrapped_heading = wrap_text(heading, heading_font, max_text_width)
    wrapped_description = wrap_text(description, desc_font, max_text_width)

    # Calculate initial positions for the heading and description
    heading_y_position = upper_rect_height + int(lower_rect_height * 0.3)
    desc_y_position = heading_y_position + heading_font_size * len(wrapped_heading) + 20  # 20 pixels space between heading and description

    # Draw the wrapped heading
    for line in wrapped_heading:
        line_width = draw.textlength(line, font=heading_font)
        line_x_position = (template_img.size[0] - line_width) // 2
        draw.text((line_x_position, heading_y_position), line, fill=heading_color, font=heading_font)
        heading_y_position += heading_font_size

    # Draw the wrapped description
    for line in wrapped_description:
        line_width = draw.textlength(line, font=desc_font)
        line_x_position = (template_img.size[0] - line_width) // 2
        draw.text((line_x_position, desc_y_position), line, fill=desc_color, font=desc_font)
        desc_y_position += desc_font_size

    final_img = template_img.resize((1024, 1024), Image.Resampling.LANCZOS)

    # Return the modified image
    return final_img


def create_ad_template_2(uploaded_image, heading, description, upper_color, lower_color, heading_color, desc_color, font_path_1, font_path_2):
    # Colors as per the new template
    # upper_color = "#F2E3CF"
    # lower_color = "#CD853F"
    
    # Create a blank square_1 image
    square_1_side = 720
    square_1 = Image.new('RGB', (square_1_side, square_1_side), 'white')
    draw = ImageDraw.Draw(square_1)
    
    # Calculate the size of the two rectangles that form square_1
    upper_rect_height = int(square_1_side * 0.45)
    lower_rect_height = square_1_side - upper_rect_height
    
    # Draw the upper rectangle
    draw.rectangle([0, 0, square_1_side, upper_rect_height], fill=upper_color)
    
    # Draw the lower rectangle
    draw.rectangle([0, upper_rect_height, square_1_side, square_1_side], fill=lower_color)

    # Create and place square_2
    square_2_side = int(0.85*(square_1_side))  # slightly less than square_1
    square_2 = Image.new('RGB', (square_2_side, square_2_side), upper_color)
    square_2_position = (square_1_side - square_2_side) // 2
    square_1.paste(square_2, (square_2_position, square_2_position))
    
    # Open the uploaded image and adjust it
    user_image = Image.open(uploaded_image).convert("RGBA")
    frame_height = int(lower_rect_height)
    adjusted_image = adjust_and_crop_image(user_image, square_2_side, frame_height, corner_radius=0)
    
    # Overlay the uploaded image onto square_2
    square_1.paste(adjusted_image, (square_2_position, square_2_position), adjusted_image)

    # Draw the text onto the lower rectangle
    draw = ImageDraw.Draw(square_1)
    
    # Load fonts
    heading_font_size = int(square_1_side*0.06)  # You can adjust the size
    desc_font_size = int(square_1_side*0.035)  # You can adjust the size
    heading_font = ImageFont.truetype(font_path_1, heading_font_size)
    desc_font = ImageFont.truetype(font_path_2, desc_font_size)
    
    # Define maximum text width
    max_text_width = square_2_side  # Text should fit within square_2
    
    # Wrap the heading and description texts
    wrapped_heading = wrap_text(heading, heading_font, max_text_width)
    wrapped_description = wrap_text(description, desc_font, max_text_width)
    
    # Initial Y position for the text
    text_y_position = square_2_position + frame_height + 20  # Adjust Y position for text start
    
    # Draw the wrapped heading
    for line in wrapped_heading:
        line_width = draw.textlength(line, font=heading_font)
        line_x_position = (square_1_side - line_width) // 2
        draw.text((line_x_position, text_y_position), line, fill=heading_color, font=heading_font)
        text_y_position += heading_font_size + 10  # Adjust spacing as needed

    # Draw the wrapped description
    for line in wrapped_description:
        line_width = draw.textlength(line, font=desc_font)
        line_x_position = (square_1_side - line_width) // 2
        draw.text((line_x_position, text_y_position), line, fill=desc_color, font=desc_font)
        text_y_position += desc_font_size + 5  # Adjust spacing as needed

    return square_1


def create_ad_template_3(uploaded_image, text_1, text_2, text_3, upper_color, lower_color, text_1_color, text_2_color, text_3_color, font_path_1, font_path_2, font_path_3):
    width, height = 1080, 1920
    
    # Create the blank design template
    template_img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(template_img)

    # Define the height for the upper and lower rectangles based on the 60:40 ratio
    upper_rect_height = int(height * 0.55)
    lower_rect_height = height - upper_rect_height

    # Draw the rectangles
    draw.rectangle([0, 0, width, upper_rect_height], fill=upper_color)  # Upper rectangle
    draw.rectangle([0, upper_rect_height, width, height], fill=lower_color)  # Lower rectangle
    
    # Define the square frame size and position it
    frame_size = min(upper_rect_height, lower_rect_height)
    frame_position = ((width - frame_size) // 2, upper_rect_height - (frame_size // 2))

    # Adjust and overlay the image onto the frame
    user_image = Image.open(uploaded_image).convert("RGBA")
    adjusted_image = adjust_and_crop_image(user_image, frame_size, frame_size)
    template_img.paste(adjusted_image, frame_position, adjusted_image)

    # Load fonts
    font_size_1 = int(height * 0.03)  # Example size for text_1 and text_3
    font_size_2 = int(height * 0.048)  # Example size for text_2
    font_size_3 = int(height * 0.025)

    font_1 = ImageFont.truetype(font_path_1, font_size_1)
    font_2 = ImageFont.truetype(font_path_2, font_size_2)
    font_3 = ImageFont.truetype(font_path_3, font_size_3)

    # Draw the texts onto the template
    # Draw text_1 at the top

    text_1_position = ((width - draw.textlength(text_1, font=font_1)) // 2, int(height/9))
    draw.text(text_1_position, text_1, fill=text_1_color, font=font_1)
    
    # Draw text_2 beneath text_1
    wrapped_text_2 = wrap_text(text_2, font_2, frame_size)
    text_2_y_position = text_1_position[1] + font_size_1 + 10  # 10 pixels below text_1

    for line in wrapped_text_2:
        line_width_2 = draw.textlength(line, font=font_2)
        line_x_position_2 = (width - line_width_2) // 2
        draw.text((line_x_position_2, text_2_y_position), line, fill=text_2_color, font=font_2)
        text_2_y_position += font_size_2

    wrapped_text_3 = wrap_text(text_3, font_3, frame_size)
    text_3_y_position = frame_position[1] + frame_size + int(height/20)  # 10 pixels below text_1

    for line in wrapped_text_3:
        line_width_3 = draw.textlength(line, font=font_3)
        line_x_position_3 = (width - line_width_3) // 2
        draw.text((line_x_position_3, text_3_y_position), line, fill=text_3_color, font=font_3)
        text_3_y_position += font_size_2

    # Draw text_3 below the image
    # text_3_y_position = frame_position[1] + frame_size + int(height/20)
    # text_3_position = ((width - draw.textlength(text_3, font=font_3)) // 2, text_3_y_position)
    # draw.text(text_3_position, text_3, fill=text_3_color, font=font_3)

    # Return the modified image
    return template_img

def create_ad_template_5(uploaded_image, testimonial, CTA, dark_color, light_color, testimonial_color, font_path_1, font_path_2):
    # Load the uploaded image and adjust its size

    TRANSPARENCY = .70  # Degree of transparency, 0-100%
    OPACITY = int(255 * TRANSPARENCY)

    user_image = Image.open(uploaded_image)
    image_size = 720  # Define the frame size
    adjusted_image = adjust_and_crop_image(user_image, image_size, image_size, 0)
    
    # Create the frame around the adjusted image
    frame_width = int(image_size * 0.01)
    framed_image = Image.new('RGBA', (image_size + 2 * frame_width, image_size + 2 * frame_width), hex_to_rgb(dark_color) + (255,))
    framed_image.paste(adjusted_image, (frame_width, frame_width))

    overlay = Image.new('RGBA', framed_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Create the quote box
    box_width = int(image_size * 0.75)
    box_height = int(image_size * 0.300)
    box_x = (framed_image.width - box_width) // 2
    box_y = image_size//2 + ((image_size // 2 - box_height) //2)
    draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], fill=hex_to_rgb(dark_color) + (OPACITY,))

    framed_image = Image.alpha_composite(framed_image, overlay)

    draw = ImageDraw.Draw(framed_image)

    # Draw the double quote
    quote_font_size = int(box_height * 0.8)
    quote_font = ImageFont.truetype(font_path_2, quote_font_size)

    quote_width = draw.textlength("“", quote_font)
    print("image_width: {}".format(frame_width))
    print("quote_width: {}".format(quote_width))

    draw.text(((image_size - quote_width)//2, box_y-50), "“", fill=light_color, font=quote_font)

    # Load fonts for the testimonial and CTA
    text_font = ImageFont.truetype(font_path_1, int(box_height * 0.1))
    cta_font = ImageFont.truetype(font_path_2, int(box_height * 0.08))

    # Wrap and draw the testimonial text
    wrapped_testimonial = wrap_text(testimonial, text_font, box_width - 40)
    wrapped_CTA = wrap_text(CTA, cta_font, box_width - 40)
    current_y = image_size * 0.7
    for line in wrapped_testimonial:
        line_width = draw.textlength(line, font=text_font)
        line_x_position = (image_size - line_width) // 2
        draw.text((line_x_position, current_y), line, fill=testimonial_color, font=text_font)
        current_y += text_font.getsize(line)[1] + 5
    
    # Draw the CTA below the testimonial
    for line in wrapped_CTA:
        line_width = draw.textlength(line, font=cta_font)
        line_x_position = (image_size - line_width) // 2
        draw.text((line_x_position, current_y+20), line, fill=testimonial_color, font=cta_font)
        current_y += cta_font.getsize(line)[1] + 5

    return framed_image


### EDITORS ###

def editor_and_layout_ad_1(uploaded_image, light_recommended_colors, dark_recommended_colors, creative_copies):
      # Set layout to use full screen width

    # Create a sidebar for image upload
    if uploaded_image:
    # Create two columns for the editor and the image display
        col1, col2, col3, col4, col5 = st.columns([1, 0.5, 0.5, 0.1, 1])
        # Editor in the first column
        with col1:
            st.header("Text Editor")
            text_1 = st.text_input("Enter the heading", creative_copies['Name'], key = 'editor_1_text_1')
            text_2 = st.text_area("Enter the main description", creative_copies['Hook'], key = 'editor_1_text_2')
            # text_3 = st.text_input("Enter the sub-description", "Great community and amenities!")

            # Font path (ensure that you have this font .ttf file in your directory or choose another)
            # font_path = "arial.ttf"

        if 'dark_color_1' not in st.session_state:
            st.session_state.dark_color_1 = dark_recommended_colors[0]  # default value
        if 'light_color_1' not in st.session_state:
            st.session_state.light_color_1 = light_recommended_colors[0]  # default value

        # light_recommended_colors = ["#D8E2DC", "#F4F1DE", "#E9D8A6", "#EE9B00", "#CA6702", "#9B2226", "#AE2012", "#BB3E03"]  # Example colors
        # dark_recommended_colors = ["#041E42", "#07283C", "#184E77", "#264653", "#2A9D8F", "#335C78", "#5F7161", "#6D597A"]  # Example colors
        fonts = ["arial.ttf","times.ttf","comic.ttf","cour.ttf","verdana.ttf","trebuc.ttf","georgia.ttf","impact.ttf",
                "tahoma.ttf","l_10646.ttf","lucon.ttf","pala.ttf","cambria.ttc","segoeui.ttf",
                # "Lato-Regular.ttf", "helvetica.ttf", "Futura.ttf","Calibri.ttf","consolas.ttf","Franklin Gothic Medium.ttf","Baskerville Old Face.ttf","Algerian.ttf",
                # "Roboto-Regular.ttf","OpenSans-Regular.ttf", "gara.ttf",
                ]

        with col2:
            st.header("Color Editor")
            dark_color_1 = st.color_picker("Pick the first color", st.session_state.dark_color_1, key = 'editor_1_color_1')
            light_color_1 = st.color_picker("Pick the second color", st.session_state.light_color_1, key = 'editor_1_color_2')
            if st.button("Use recommended colors", key = 'editor_1_recommend'):
                # Update colors with random recommended ones
                st.session_state.dark_color_1 = random.choice(dark_recommended_colors)
                st.session_state.light_color_1 = random.choice(light_recommended_colors)

                dark_color_1 = st.session_state.dark_color_1
                light_color_1 = st.session_state.light_color_1

            heading_color = st.color_picker("Pick a color for the heading text", "#000000", key = 'editor_1_color_3')
            description_color = st.color_picker("Pick a color for the description text", "#000000", key = 'editor_1_color_4')

            # text_3_color = st.color_picker("Pick the third text color", "#000000")
            # Check if all inputs are provided

        with col3:
            st.header("Font Editor")
            font_path_1 = st.selectbox("Select a font", fonts, index=fonts.index("arial.ttf"), key='editor_1_font_1')
            font_path_2 = st.selectbox("Select a font", fonts, index=fonts.index("arial.ttf"), key='editor_1_font_2')
            # font_path_3 = st.selectbox("Select a font", fonts, index=fonts.index("arial.ttf"), key='font_3')
        
        # if uploaded_image and text_1 and text_2:
        #     # Call the function to create the ad template
        #     # def create_ad_template(uploaded_image, heading, description, upper_color, lower_color, heading_color, desc_color, font_path_1, font_path_2):
        #     result_image = create_ad_template(image, text_1, text_2, upper_color, lower_color, heading_color, description_color, font_path_1, font_path_2)
            
            # Display button to generate ad
            # if st.button('Generate Ad'):
            #     # Display the result in the second column
        if uploaded_image and text_1 and text_2:
            result_image = create_ad_template_1(uploaded_image, text_1, text_2, dark_color_1, light_color_1, heading_color, description_color, font_path_1, font_path_2)
            img_byte_arr = BytesIO()
            result_image.save(img_byte_arr, format='PNG')  # Using PNG format
            img_byte_arr = img_byte_arr.getvalue()

            # Encode image to base64
            base64_encoded_result = base64.b64encode(img_byte_arr)
            base64_string = base64_encoded_result.decode('utf-8')
            
            with col5:
                st.image(result_image, width=400)
                if st.button('Prepare High-Quality Image for Download', key = 'editor_1_download'):
                    with st.spinner('Preparing your high-quality image...'):
                        high_quality_image = download_image(result_image)

                    st.download_button(
                        label="Download Image",
                        data=high_quality_image,
                        file_name="creative.png",
                        mime="image/png"
                    )
        
            return result_image, base64_string


def editor_and_layout_ad_2(uploaded_image, light_recommended_colors, dark_recommended_colors, creative_copies):
    # Create a sidebar for image upload
    if uploaded_image:
        # Create columns for the editor and the image display
        col1, col2, col3, col4, col5 = st.columns([1, 0.5, 0.5, 0.1, 1])
        
        # Editor in the first column
        with col1:
            st.header("Text Editor")
            text_1 = st.text_input("Enter the heading", creative_copies['Name'], key = 'editor_2_text_1')
            text_2 = st.text_area("Enter the main description", creative_copies['Hook'], key = 'editor_2_text_2')
        
        if 'light_color_2' not in st.session_state:
            st.session_state.light_color_2 = light_recommended_colors[0] # default value
        if 'dark_color_2' not in st.session_state:
            st.session_state.dark_color_2 = dark_recommended_colors[0]  # default value

        # light_recommended_colors = ["#D8E2DC", "#F4F1DE", "#E9D8A6", "#EE9B00", "#CA6702", "#9B2226", "#AE2012", "#BB3E03"]  # Example colors
        # dark_recommended_colors = ["#041E42", "#07283C", "#184E77", "#264653", "#2A9D8F", "#335C78", "#5F7161", "#6D597A"]  # Example colors
        fonts = ["arial.ttf","times.ttf","comic.ttf","cour.ttf","verdana.ttf","trebuc.ttf","georgia.ttf","impact.ttf",
    "tahoma.ttf","l_10646.ttf","lucon.ttf","pala.ttf","cambria.ttc","segoeui.ttf",
    # "Lato-Regular.ttf", "helvetica.ttf", "Futura.ttf","Calibri.ttf","consolas.ttf","Franklin Gothic Medium.ttf","Baskerville Old Face.ttf","Algerian.ttf",
    # "Roboto-Regular.ttf","OpenSans-Regular.ttf", "gara.ttf",
    ]

        # Color Editor in the second column
        with col2:
            st.header("Color Editor")
            light_color_2 = st.color_picker("Pick the first color", st.session_state.light_color_2, key = 'editor_2_color_1')
            dark_color_2 = st.color_picker("Pick the second color", st.session_state.dark_color_2, key = 'editor_2_color_2')
            if st.button("Use recommended colors", key = 'editor_2_recommend'):
                # Update colors with random recommended ones
                st.session_state.light_color_2 = random.choice(light_recommended_colors)
                st.session_state.dark_color_2 = random.choice(dark_recommended_colors)
                light_color_2 = st.session_state.light_color_2
                dark_color_2 = st.session_state.dark_color_2
            heading_color = st.color_picker("Pick a color for the heading text", "#000000", key = 'editor_2_color_3')
            description_color = st.color_picker("Pick a color for the description text", "#000000", key = 'editor_2_color_4')

        # Font Editor in the third column
        with col3:
            st.header("Font Editor")
            font_path_1 = st.selectbox("Select a font for the heading", fonts, index=fonts.index("arial.ttf"), key='editor_2_font_1')
            font_path_2 = st.selectbox("Select a font for the description", fonts, index=fonts.index("arial.ttf"), key='editor_2_font_2')

        # Display the ad template and download options in the fifth column
        if uploaded_image and text_1 and text_2:
            result_image = create_ad_template_2(uploaded_image, text_1, text_2, light_color_2, dark_color_2, heading_color, description_color, font_path_1, font_path_2)
            # Convert PIL Image to Bytes

            img_byte_arr = BytesIO()
            result_image.save(img_byte_arr, format='PNG')  # Using PNG format
            img_byte_arr = img_byte_arr.getvalue()

            # Encode image to base64
            base64_encoded_result = base64.b64encode(img_byte_arr)
            base64_string = base64_encoded_result.decode('utf-8')
                
            with col5:
                st.image(result_image, width=400)
                if st.button('Prepare High-Quality Image for Download', key = 'editor_2_download'):
                    with st.spinner('Preparing your high-quality image...'):
                        high_quality_image = download_image(result_image)

                    st.download_button(
                        label="Download Image",
                        data=high_quality_image,
                        file_name="creative.png",
                        mime="image/png"
                    )

            return result_image, base64_string

def editor_and_layout_ad_3(uploaded_image, light_recommended_colors, dark_recommended_colors, creative_copies):
      # Set layout to use full screen width

    # Create a sidebar for image upload
    if uploaded_image:
    # Create two columns for the editor and the image display
        col1, col2, col3, col4, col5 = st.columns([1, 0.5, 0.5, 0.1, 1])

        # Editor in the first column
        with col1:
            st.header("Text Editor")
            text_1 = st.text_input("Enter the heading", creative_copies['Name'], key = 'editor_3_text_1')
            text_2 = st.text_area("Enter the main description", creative_copies['Hook'], key = 'editor_3_text_2')
            text_3 = st.text_input("Enter the sub-description", creative_copies['Sub Description'], key = 'editor_3_text_3')

        if 'dark_color_3' not in st.session_state:
            st.session_state.dark_color_3 = dark_recommended_colors[0]  # default value
        if 'light_color_3' not in st.session_state:
            st.session_state.light_color_3 = light_recommended_colors[0]  # default value

        # light_recommended_colors = ["#D8E2DC", "#F4F1DE", "#E9D8A6", "#EE9B00", "#CA6702", "#9B2226", "#AE2012", "#BB3E03"]  # Example colors
        # dark_recommended_colors = ["#041E42", "#07283C", "#184E77", "#264653", "#2A9D8F", "#335C78", "#5F7161", "#6D597A"]  # Example colors
        fonts = ["arial.ttf","times.ttf","comic.ttf","cour.ttf","verdana.ttf","trebuc.ttf","georgia.ttf","impact.ttf",
                "tahoma.ttf","l_10646.ttf","lucon.ttf","pala.ttf","cambria.ttc","segoeui.ttf",
                # "Lato-Regular.ttf", "helvetica.ttf", "Futura.ttf","Calibri.ttf","consolas.ttf","Franklin Gothic Medium.ttf","Baskerville Old Face.ttf","Algerian.ttf",
                # "Roboto-Regular.ttf","OpenSans-Regular.ttf", "gara.ttf",
                ]
            # Font path (ensure that you have this font .ttf file in your directory or choose another)

        with col2:
            st.header("Color Editor")
            dark_color_3 = st.color_picker("Pick the first color", st.session_state.dark_color_3, key = 'editor_3_color_1')
            light_color_3 = st.color_picker("Pick the second color", st.session_state.light_color_3, key = 'editor_3_color_2')
            if st.button("Use recommended colors", key = 'editor_3_recommend'):
                # Update colors with random recommended ones
                st.session_state.dark_color_3 = random.choice(dark_recommended_colors)
                st.session_state.light_color_3 = random.choice(light_recommended_colors)
                dark_color_3 = st.session_state.dark_color_3
                light_color_3 = st.session_state.light_color_3
            text_1_color = st.color_picker("Pick the first text color", "#FFFFFF", key = 'editor_3_color_3')
            text_2_color = st.color_picker("Pick the second text color", "#FFFFFF", key = 'editor_3_color_4')
            text_3_color = st.color_picker("Pick the third text color", "#000000", key = 'editor_3_color_5')
            # Check if all inputs are provided

        with col3:
            st.header("Font Editor")
            font_path_1 = st.selectbox("Select a font", fonts, index=fonts.index("arial.ttf"), key='editor_3_font_1')
            font_path_2 = st.selectbox("Select a font", fonts, index=fonts.index("arial.ttf"), key='editor_3_font_2')
            font_path_3 = st.selectbox("Select a font", fonts, index=fonts.index("arial.ttf"), key='editor_3_font_3')

        
        if uploaded_image and text_1 and text_2:
            result_image = create_ad_template_3(uploaded_image, text_1, text_2, text_3, dark_color_3, light_color_3, text_1_color, text_2_color, text_3_color, font_path_1, font_path_2, font_path_3)
            img_byte_arr = BytesIO()
            result_image.save(img_byte_arr, format='PNG')  # Using PNG format
            img_byte_arr = img_byte_arr.getvalue()

            # Encode image to base64
            base64_encoded_result = base64.b64encode(img_byte_arr)
            base64_string = base64_encoded_result.decode('utf-8')
            
            with col5:
                st.image(result_image, width=400)
                if st.button('Prepare High-Quality Image for Download', key = 'editor_3_download'):
                    with st.spinner('Preparing your high-quality image...'):
                        high_quality_image = download_image(result_image)

                    st.download_button(
                        label="Download Image",
                        data=high_quality_image,
                        file_name="creative.png",
                        mime="image/png"
                    )

            return result_image, base64_string



def editor_and_layout_ad_5(uploaded_image, light_recommended_colors, dark_recommended_colors, creative_copies):
      # Set layout to use full screen width

    # Create a sidebar for image upload
    if uploaded_image:
    # Create two columns for the editor and the image display
        col1, col2, col3, col4, col5 = st.columns([1, 0.5, 0.5, 0.1, 1])
        # Editor in the first column
        with col1:
            st.header("Text Editor")
            testimonial = st.text_area("Enter the heading", creative_copies['Testimonial'], key = 'editor_5_text_1')
            CTA = st.text_area("Enter the main description", creative_copies['CTA'], key = 'editor_5_text_2')
            # text_3 = st.text_input("Enter the sub-description", "Great community and amenities!")

            # Font path (ensure that you have this font .ttf file in your directory or choose another)
            # font_path = "arial.ttf"

        if 'dark_color_1' not in st.session_state:
            st.session_state.dark_color_1 = dark_recommended_colors[0]  # default value
        if 'light_color_1' not in st.session_state:
            st.session_state.light_color_1 = light_recommended_colors[0]  # default value

        # light_recommended_colors = ["#D8E2DC", "#F4F1DE", "#E9D8A6", "#EE9B00", "#CA6702", "#9B2226", "#AE2012", "#BB3E03"]  # Example colors
        # dark_recommended_colors = ["#041E42", "#07283C", "#184E77", "#264653", "#2A9D8F", "#335C78", "#5F7161", "#6D597A"]  # Example colors
        # fonts = ["arial.ttf","times.ttf","comic.ttf","cour.ttf","verdana.ttf","trebuc.ttf","georgia.ttf","impact.ttf",
        #         "tahoma.ttf","l_10646.ttf","lucon.ttf","pala.ttf","cambria.ttc","segoeui.ttf",
        #         # "Lato-Regular.ttf", "helvetica.ttf", "Futura.ttf","Calibri.ttf","consolas.ttf","Franklin Gothic Medium.ttf","Baskerville Old Face.ttf","Algerian.ttf",
        #         # "Roboto-Regular.ttf","OpenSans-Regular.ttf", "gara.ttf",
        #         ]

        fonts = [f for f in os.listdir(font_dir) if f.endswith(('.ttf', '.otf'))]

        with col2:
            st.header("Color Editor")
            dark_color_1 = st.color_picker("Pick the dark color", st.session_state.dark_color_1, key = 'editor_5_color_1')
            light_color_1 = st.color_picker("Pick the light color", st.session_state.light_color_1, key = 'editor_5_color_2')
            if st.button("Use recommended colors", key = 'editor_5_recommend'):
                # Update colors with random recommended ones
                st.session_state.dark_color_1 = random.choice(dark_recommended_colors)
                st.session_state.light_color_1 = random.choice(light_recommended_colors)

                dark_color_1 = st.session_state.dark_color_1
                light_color_1 = st.session_state.light_color_1

            heading_color = st.color_picker("Pick a color for the text", "#FFFFFF", key = 'editor_5_color_3')
            # description_color = st.color_picker("Pick a color for the description text", "#000000", key = 'editor_1_color_4')

            # text_3_color = st.color_picker("Pick the third text color", "#000000")
            # Check if all inputs are provided

        with col3:
            st.header("Font Editor")
            font_path_1 = st.selectbox("Select a font for the Testimonial", fonts, index=fonts.index("arial.ttf"), key='editor_5_font_1')
            font_path_2 = st.selectbox("Select a CTA", fonts, index=fonts.index("arial.ttf"), key='editor_5_font_2')
            # font_path_3 = st.selectbox("Select a font", fonts, index=fonts.index("arial.ttf"), key='font_3')
        
        # if uploaded_image and text_1 and text_2:
        #     # Call the function to create the ad template
        #     # def create_ad_template(uploaded_image, heading, description, upper_color, lower_color, heading_color, desc_color, font_path_1, font_path_2):
        #     result_image = create_ad_template(image, text_1, text_2, upper_color, lower_color, heading_color, description_color, font_path_1, font_path_2)
            
            # Display button to generate ad
            # if st.button('Generate Ad'):
            #     # Display the result in the second column
        if uploaded_image and testimonial and CTA:
            result_image = create_ad_template_5(uploaded_image, testimonial, CTA, dark_color_1, light_color_1, heading_color, font_path_1, font_path_2)
            img_byte_arr = BytesIO()
            result_image.save(img_byte_arr, format='PNG')  # Using PNG format
            img_byte_arr = img_byte_arr.getvalue()

            # Encode image to base64
            base64_encoded_result = base64.b64encode(img_byte_arr)
            base64_string = base64_encoded_result.decode('utf-8')
            
            with col5:
                st.image(result_image, width=400)
                if st.button('Prepare High-Quality Image for Download', key = 'editor_5_download'):
                    with st.spinner('Preparing your high-quality image...'):
                        high_quality_image = download_image(result_image)

                    st.download_button(
                        label="Download Image",
                        data=high_quality_image,
                        file_name="creative.png",
                        mime="image/png"
                    )
        
            return result_image, base64_string
        


