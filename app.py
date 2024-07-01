import streamlit as st
import os
import re
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text, create_thread_with_message, run_thread, send_message_to_thread
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Float feature initialization
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

initialize_session_state()

st.title("Drive Thru Assistant")

# Create footer container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    # Write the audio bytes to a file
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

if st.session_state.messages and st.session_state.messages[0]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("🤔🤔🤔..."):
            final_response = get_answer(st.session_state.messages)
        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.write(final_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": final_response}
        )
        os.remove(audio_file)

        # Create a new thread or send a message to the existing thread
        if not st.session_state.thread_id:
            st.session_state.thread_id = create_thread_with_message(st.session_state.messages)
            run_thread(st.session_state.thread_id)
        else:
            send_message_to_thread(st.session_state.thread_id, final_response)

# Display the updated order table
if st.session_state.thread_id:
    with st.spinner("Fetching updated order..."):
        order_summary = send_message_to_thread(st.session_state.thread_id, "Get order summary")
        st.markdown(order_summary)

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")
