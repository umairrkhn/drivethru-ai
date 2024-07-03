import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock

# Float feature initialization
float_init()


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


initialize_session_state()

st.title("Drive Thru Assistant")

# Initialize client, assistant and thread_id in session_state
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(assistant_id=st.secrets["ASSISTANT_ID"])
if "thread_id" not in st.session_state:
    st.session_state.thread_id = client.beta.threads.create().id

# Adding a new container for the assistant's recent message
assistant_msg_container = st.container()

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

            # Add user query to the thread
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=final_response,
            )

            # Stream the assistant's reply
            stream = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=st.secrets["ASSISTANT_ID"],
                stream=True,
            )

        # A blank string to store the assistant's reply
        assistant_reply = ""

        # Iterate through the stream
        for event in stream:
            # Consider if there's a delta text
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    # Add the new text to assistant_reply
                    assistant_reply += event.data.delta.content[0].text.value

        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.write(final_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": final_response}
        )
        os.remove(audio_file)

    # Add assistant's recent response under 'Order'
    if assistant_reply:
        with assistant_msg_container:
            st.subheader("Order")
            st.text(assistant_reply)

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")
