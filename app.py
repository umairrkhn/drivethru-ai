import streamlit as st
import os
import utils
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock

# Float feature initialization
float_init()

# Define a layout hack
st.markdown(
    """
    <style>
    .reportview-container {
        flex-direction: row;
        flex-wrap: wrap;
    }
    .block-container {
        width: 70%;
    }
    .sidebar .sidebar-content {
        width: 30%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


initialize_session_state()

st.title("Drive Thru Assistant")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(assistant_id=st.secrets["ASSISTANT_ID"])
if "thread_id" not in st.session_state:
    st.session_state.thread_id = client.beta.threads.create().id

footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    with st.spinner("Transcribing..."):
        audio_file_path = "temp_audio.mp3"
        with open(audio_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = utils.speech_to_text(audio_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(audio_file_path)

if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("🤔🤔🤔..."):
            final_response = utils.get_answer(st.session_state.messages)
            st.session_state.messages.append(
                {"role": "assistant", "content": final_response}
            )

            st.write(final_response)

            audio_file = utils.text_to_speech(final_response)
            utils.autoplay_audio(audio_file)
            os.remove(audio_file)

st.sidebar.subheader("Order")
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    st.sidebar.text(st.session_state.messages[-1]["content"])

footer_container.float("bottom: 0rem;")
