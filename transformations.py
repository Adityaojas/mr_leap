from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap

def wrap_text(text, font, max_width):
    """
    Wraps text so that it fits within a specified width when drawn.
    Returns a list of lines.
    """
    draw = ImageDraw.Draw(Image.new('RGB', (10, 10)))  # Temp image for measuring text
    lines = textwrap.wrap(text, width=50)  # Initial wrap to avoid extremely long words issue
    wrapped_lines = []

    print('wrapped lines: '.format(wrapped_lines))

    for line in lines:
        # Measure line width
        line_width = draw.textlength(line, font=font)
        
        # If the line is too wide, split it further
        if line_width > max_width:
            words = line.split()
            new_line = ''
            while words:
                # Here we ensure we're concatenating strings, not a string with a list
                potential_new_line = new_line + words[0] + ' ' # Append next word
                # Check the width of the potential new line
                if draw.textlength(potential_new_line, font=font) <= max_width:
                    new_line = potential_new_line
                    words.pop(0)  # Remove the word that's just been added
                else:
                    # If the line is too wide, add it to wrapped lines and start a new line
                    wrapped_lines.append(new_line.strip())
                    new_line = ''
            # If any words remain that do not exceed the max_width, add them as a line
            if new_line:
                wrapped_lines.append(new_line.strip())
        else:
            wrapped_lines.append(line)
    return wrapped_lines


def add_rounded_corners(image, corner_radius):
    """
    Adds rounded corners to an image.
    """
    # Create a mask with rounded corners
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image.size, radius=corner_radius, fill=255)
    
    # Apply the rounded mask to the image
    rounded_image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)
    
    return rounded_image

def adjust_and_crop_image(image, target_width, target_height, corner_radius=40):
    """
    Adjusts an image's size to fit a specified frame (target_width x target_height)
    without distorting its aspect ratio. Crops the image if necessary to ensure it
    fits within the target dimensions.
    """
    # Calculate the target aspect ratio
    target_aspect_ratio = target_width / target_height

    # Calculate the image's aspect ratio
    original_width, original_height = image.size
    image_aspect_ratio = original_width / original_height

    # Determine how to resize the image
    if image_aspect_ratio > target_aspect_ratio:
        # Image is wider than the target frame, resize based on height
        new_height = target_height
        new_width = int(new_height * image_aspect_ratio)
    else:
        # Image is taller or equal in aspect ratio, resize based on width
        new_width = target_width
        new_height = int(new_width / image_aspect_ratio)

    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate the coordinates for cropping
    left = (resized_image.width - target_width) / 2
    top = (resized_image.height - target_height) / 2
    right = (resized_image.width + target_width) / 2
    bottom = (resized_image.height + target_height) / 2

    # Crop the image
    cropped_image = resized_image.crop((left, top, right, bottom))

    image_with_rounded_corners = add_rounded_corners(cropped_image, corner_radius)
    
    return image_with_rounded_corners


def create_banner_ad_1(uploaded_image, heading, description, heading_color, desc_color, font_path):
    # Colors as per the template
    dark_brown = "#CD853F"
    light_brown = "#F2E3CF"
    
    # Create a blank template image
    template_img = Image.new('RGB', (768, 768), dark_brown)
    draw = ImageDraw.Draw(template_img)
    
    # Calculate the size of the two rectangles
    upper_rect_height = int(template_img.size[1] * 0.6)
    lower_rect_height = template_img.size[1] - upper_rect_height
    
    # Draw the light brown rectangle
    draw.rectangle([0, upper_rect_height, template_img.size[0], template_img.size[1]], fill=light_brown)

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
    desc_font_size = int(lower_rect_height * 0.08)
    heading_font = ImageFont.truetype(font_path, heading_font_size)
    desc_font = ImageFont.truetype(font_path, desc_font_size)

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

    # Return the modified image
    return template_img

# def st_editor_banner_ad_1(heading_init, description_init, heading_color_init, description_color_init, font_init):
#     # Text inputs
#     heading_text = st.text_input("Enter the heading", "INDOHOMZ")
#     description_text = st.text_input("Enter the description", "Studio apartments in Gurgaon starting at just Rs. 26,000!")
#     heading_color = st.color_picker("Pick a color for the heading text", "#000000")
#     description_color = st.color_picker("Pick a color for the description text", "#000000")

#     # Font path (ensure that you have this font .ttf file in your directory or choose another)
#     font_path = "arial.ttf"

#     return heading_text, description_text, heading_color,

# def create_banner_ad_2(uploaded_image, heading, description, heading_color, desc_color, font_path):
#     # Colors as per the new template
#     upper_color = "#F2E3CF"
#     lower_color = "#CD853F"
    
#     # Create a blank square_1 image
#     square_1_side = 768
#     square_1 = Image.new('RGB', (square_1_side, square_1_side), 'white')
#     draw = ImageDraw.Draw(square_1)
    
#     # Calculate the size of the two rectangles that form square_1
#     upper_rect_height = int(square_1_side * 0.45)
#     lower_rect_height = square_1_side - upper_rect_height
    
#     # Draw the upper rectangle
#     draw.rectangle([0, 0, square_1_side, upper_rect_height], fill=upper_color)
    
#     # Draw the lower rectangle
#     draw.rectangle([0, upper_rect_height, square_1_side, square_1_side], fill=lower_color)

#     # Create and place square_2
#     square_2_side = int(0.85*(square_1_side))  # slightly less than square_1
#     square_2 = Image.new('RGB', (square_2_side, square_2_side), upper_color)
#     square_2_position = (square_1_side - square_2_side) // 2
#     square_1.paste(square_2, (square_2_position, square_2_position))
    
#     # Open the uploaded image and adjust it
#     user_image = Image.open(uploaded_image).convert("RGBA")
#     frame_height = int(lower_rect_height)
#     adjusted_image = adjust_and_crop_image(user_image, square_2_side, frame_height, corner_radius=0)
    
#     # Overlay the uploaded image onto square_2
#     square_1.paste(adjusted_image, (square_2_position, square_2_position), adjusted_image)

#     # Draw the text onto the lower rectangle
#     draw = ImageDraw.Draw(square_1)
    
#     # Load fonts
#     heading_font_size = 40  # You can adjust the size
#     desc_font_size = 20  # You can adjust the size
#     heading_font = ImageFont.truetype(font_path, heading_font_size)
#     desc_font = ImageFont.truetype(font_path, desc_font_size)
    
#     # Define maximum text width
#     max_text_width = square_2_side  # Text should fit within square_2
    
#     # Wrap the heading and description texts
#     wrapped_heading = wrap_text(heading, heading_font, max_text_width)
#     wrapped_description = wrap_text(description, desc_font, max_text_width)
    
#     # Initial Y position for the text
#     text_y_position = square_2_position + frame_height + 20  # Adjust Y position for text start
    
#     # Draw the wrapped heading
#     for line in wrapped_heading:
#         line_width = draw.textlength(line, font=heading_font)
#         line_x_position = (square_1_side - line_width) // 2
#         draw.text((line_x_position, text_y_position), line, fill=heading_color, font=heading_font)
#         text_y_position += heading_font_size + 10  # Adjust spacing as needed

#     # Draw the wrapped description
#     for line in wrapped_description:
#         line_width = draw.textlength(line, font=desc_font)
#         line_x_position = (square_1_side - line_width) // 2
#         draw.text((line_x_position, text_y_position), line, fill=desc_color, font=desc_font)
#         text_y_position += desc_font_size + 5  # Adjust spacing as needed

#     return square_1

# def create_story_ad(uploaded_image, text_1, text_2, text_3, font_path):
#     width, height = 1080, 1920
    
#     # Create the blank design template
#     template_img = Image.new('RGB', (width, height))
#     draw = ImageDraw.Draw(template_img)

#     # Define the height for the upper and lower rectangles based on the 60:40 ratio
#     upper_rect_height = int(height * 0.55)
#     lower_rect_height = height - upper_rect_height

#     # Draw the rectangles
#     draw.rectangle([0, 0, width, upper_rect_height], fill='#2c441a')  # Upper rectangle
#     draw.rectangle([0, upper_rect_height, width, height], fill='#d6ddd1')  # Lower rectangle
    
#     # Define the square frame size and position it
#     frame_size = min(upper_rect_height, lower_rect_height)
#     frame_position = ((width - frame_size) // 2, upper_rect_height - (frame_size // 2))

#     # Adjust and overlay the image onto the frame
#     user_image = Image.open(uploaded_image).convert("RGBA")
#     adjusted_image = adjust_and_crop_image(user_image, frame_size, frame_size)
#     template_img.paste(adjusted_image, frame_position, adjusted_image)

#     # Load fonts
#     font_size_1 = int(height * 0.03)  # Example size for text_1 and text_3
#     font_size_2 = int(height * 0.048)  # Example size for text_2
#     font_size_3 = int(height * 0.025)

#     font_1 = ImageFont.truetype(font_path, font_size_1)
#     font_2 = ImageFont.truetype(font_path, font_size_2)
#     font_3 = ImageFont.truetype(font_path, font_size_3)

#     # Draw the texts onto the template
#     # Draw text_1 at the top
#     text_1_position = ((width - draw.textlength(text_1, font=font_1)) // 2, int(height/9))
#     draw.text(text_1_position, text_1, fill="white", font=font_1)
    
#     # Draw text_2 beneath text_1
#     wrapped_text_2 = wrap_text(text_2, font_2, frame_size)
#     text_2_y_position = text_1_position[1] + font_size_1 + 10  # 10 pixels below text_1

#     for line in wrapped_text_2:
#         line_width = draw.textlength(line, font=font_2)
#         line_x_position = (width - line_width) // 2
#         draw.text((line_x_position, text_2_y_position), line, fill="white", font=font_2)
#         text_2_y_position += font_size_2

#     # Draw text_3 below the image
#     text_3_y_position = frame_position[1] + frame_size + int(height/20)
#     text_3_position = ((width - draw.textlength(text_3, font=font_3)) // 2, text_3_y_position)
#     draw.text(text_3_position, text_3, fill="black", font=font_3)

#     # Return the modified image
#     return template_img



