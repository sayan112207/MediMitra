from dotenv import load_dotenv
load_dotenv() #loading all the environment variables

import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model=genai.GenerativeModel("gemini-pro") 
chat = model.start_chat(history=[])


def get_gemini_response(question):
    response=chat.send_message(question,stream=True)
    return response


st.set_page_config(
    page_title="MediMitra",
    page_icon="🩺",
    initial_sidebar_state="expanded",
)

from PIL import Image

# Open the image file
img = Image.open('bot.png')

# Convert the image to base64
import base64
from io import BytesIO

buffered = BytesIO()
img.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# Display the image in the center
st.markdown(f'<p style="text-align: center;"><img src="data:image/png;base64,{img_str}" width="120"></p>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black;'>MediMitra</h1>", unsafe_allow_html=True)
#st.header("MediMitra")

from streamlit_mic_recorder import mic_recorder,speech_to_text

state=st.session_state


if 'text_received' not in state:
    state.text_received=[]

c1, c2, c3 = st.columns([1,2,1])  # Create three columns
with c2:  # Use the middle column for the button
    text=speech_to_text(language='en',use_container_width=True,just_once=True,key='STT')

if text:       
    state.text_received.append(text)

for text in state.text_received:
    st.text(text)

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'input_key' not in st.session_state:
    st.session_state['input_key'] = 0

if text:
    user_input = text 
else:
    user_input = st.text_input("How are you feeling today: ", key=f"user_input_{st.session_state['input_key']}")

submit=st.button("Ask")
clear=st.button("Clear ")

# Add an image upload button
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# If an image is uploaded, convert it to base64 and use it as the user input
if uploaded_file is not None:
    model=genai.GenerativeModel("gemini-pro-vision")
    img = Image.open(uploaded_file)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Display the uploaded image
    st.image(img, caption='Uploaded Image')

    response=model.generate_content(["Explain this: ",img])
    
    st.subheader("Response:")
    with st.expander("Bot's Response"):
        for chunk in response:
            st.markdown(chunk.text, unsafe_allow_html=True)
            st.session_state['chat_history'].append(("Bot", chunk.text))

if clear:
    st.session_state['text_received'] = []
    st.session_state['chat_history'] = []
    st.session_state['input_key'] += 1
    st.session_state['uploaded_image'] = None

if submit and user_input:
    response = get_gemini_response(user_input)
    st.subheader("Response:")
    with st.expander("Bot's Response"):
        for chunk in response:
            st.markdown(chunk.text, unsafe_allow_html=True)
            st.session_state['chat_history'].append(("Bot", chunk.text))


