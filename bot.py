## imports

from dotenv import load_dotenv

load_dotenv()  # loading all the environment variables
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import base64
from io import BytesIO
from streamlit_mic_recorder import mic_recorder, speech_to_text


## API KEY AND GETTING THE MODEL
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash-latest")
chat = model.start_chat(history=[])


def get_gemini_response(question):
    with st.spinner('Getting response...'):
        response = chat.send_message(question, stream=True)
    return response


## STREAMLIT STYLISTIC ELEMENTS---

st.set_page_config(
    page_title="MediMitra",
    page_icon="🩺",
    initial_sidebar_state="expanded",
)

# ADD IMAGE
img = Image.open("bot.png")
buffered = BytesIO()  # Convert the image to base64
img.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()
st.markdown(
    f'<p style="text-align: center;"><img src="data:image/png;base64,{img_str}" width="120"></p>',
    unsafe_allow_html=True,
)  # Display the image in the center

st.markdown(
    "<h1 style='text-align: center; color: black;'>MediMitra</h1>",
    unsafe_allow_html=True,
)  # st.header("MediMitra")


state = st.session_state
if "text_received" not in state:
    state.text_received = []
# Create three columns with relative widths 1:2:1
c1, c2, c3 = st.columns([1, 2, 1])

# In the middle column, convert speech to text
with c2:
    text = speech_to_text(
        language="en", use_container_width=True, just_once=True, key="STT"
    )

# If text is received, append it to the state's text_received list
if text:
    state.text_received.append(text)








# Display all received texts
for text in state.text_received:
    st.text(text)

# If chat_history is not in the session state, initialize it as an empty list
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# If input_key is not in the session state, initialize it as 0
if "input_key" not in st.session_state:
    st.session_state["input_key"] = 0

# If text is received, use it as user input, otherwise ask for user input
if text:
    user_input = text
else:
    user_input = st.text_input(
        "How are you feeling today: ", key=f"user_input_{st.session_state['input_key']}"
    )

submit = st.button("Ask")
clear = st.button("Clear ")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# If an image is uploaded, convert it to base64 and use it as the user input
if uploaded_file is not None:
    model = genai.GenerativeModel("gemini-pro-vision")
    img = Image.open(uploaded_file)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Display the uploaded image
    st.image(img, caption="Uploaded Image")

    with st.spinner('Generating content...'):
        response = model.generate_content(["Explain this: ", img])

    st.subheader("Response:")
    with st.expander("Bot's Response"):
        for chunk in response:
            st.markdown(chunk.text, unsafe_allow_html=True)
            st.session_state["chat_history"].append(("Bot", chunk.text))


# On pressing the Clear button, the chat history and input key are reset. And everything starts from 0
if clear:
    st.session_state["text_received"] = []
    st.session_state["chat_history"] = []
    st.session_state["input_key"] += 1
    st.session_state["uploaded_image"] = None


if submit and user_input:  # submit button is clicked as well as user_input is not null.
    with st.spinner('Getting response...'):
        response = get_gemini_response(user_input)  # asking the model for response

    st.subheader("Response:")
    with st.expander("Bot's Response"):
        for chunk in response:
            st.markdown(chunk.text, unsafe_allow_html=True)
            st.session_state["chat_history"].append(("Bot", chunk.text))
