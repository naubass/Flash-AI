import streamlit as st
import os
from google.genai import types
from google import genai
import time
from PyPDF2 import PdfMerger
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

def setup_app():
    st.set_page_config(
        page_title="⚡ Flash-AI",
        layout="centered"
    )

    st.header("Selamat Datang di ⚡ Flash-AI")
    st.sidebar.header("Options", divider="rainbow")

def get_choice():
    return st.sidebar.radio("Choose:", [
        "Ayok Mulai Chat",
        "Upload PDF Kamu",
        "Upload Multiple PDF",
        "Upload Image/Gambar",
        "Upload Audio/mp3",
        "Upload Video/mp4"
    ])

def get_clear():
    return st.sidebar.button("Session Obrolan Baru", key="clear")

def upload_temp_file(uploaded_file, temp_name):
    """Save uploaded file to local temp file for uploading to genai client"""
    with open(temp_name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_name

def main():
    choice = get_choice()
    clear = get_clear()

    if clear:
        if 'messages' in st.session_state:
            del st.session_state['messages']
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # setup API key google
    api_key =  st.secrets('GOOGLE_API_KEY_NEW')
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-2.5-flash"

    if choice == "Ayok Mulai Chat":
        st.subheader("Apa yang ingin kamu ketahui?😊")
        system_instruction = """
            You are a helpful, informative assistant. 
            Give clear, complete, and user-friendly responses. 
            If the user asks for details, provide explanations or examples.
        """

        if not st.session_state['messages']:
            chat = client.chats.create(
                model=MODEL_ID,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            st.session_state['chat'] = chat

        prompt = st.chat_input("Enter your question here")
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)
            st.session_state['messages'].append({"role": "user", "content": prompt})

            # Cek apakah pengguna minta gambar
            if "generate image" in prompt.lower() or "buat gambar" in prompt.lower():
                image_model = "gemini-2.0-flash-preview-image-generation"
                response = client.models.generate_content(
                    model=image_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"]
                    )
                )
                for part in response.candidates[0].content.parts:
                    if part.text:
                        with st.chat_message("model", avatar="🧞‍♀️"):
                            st.markdown(part.text)
                    elif part.inline_data:
                        with st.chat_message("model", avatar="🧞‍♀️"):
                            st.image(part.inline_data.data)
            else:
                chat = st.session_state.get("chat")
                response = chat.send_message(prompt)
                with st.chat_message("model", avatar="🧞‍♀️"):
                    st.markdown(response.text)
            st.session_state['messages'].append({"role": "model", "content": response.text if hasattr(response, 'text') else ""})

    elif choice == "Upload PDF Kamu":
        st.subheader("Apa yang perlu saya bantu dengan file kamu?")
        uploaded_file = st.file_uploader("Choose your PDF file", type=["pdf"])
        if uploaded_file:
            temp_pdf_path = upload_temp_file(uploaded_file, "temp_uploaded.pdf")
            file_upload = client.files.upload(file=temp_pdf_path)
            chat2 = client.chats.create(model=MODEL_ID,
                history=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=file_upload.uri,
                                mime_type=file_upload.mime_type
                            )
                        ]
                    )
                ]
            )
            prompt = st.chat_input("Enter your question here")
            if prompt:
                with st.chat_message("user"):
                    st.write(prompt)
                response = chat2.send_message(prompt)
                with st.chat_message("model", avatar="🧞‍♀️"):
                    st.markdown(response.text)
        
    elif choice == "Upload Multiple PDF":
        st.subheader("Kamu bisa Upload Banyak File disini")
        uploaded_file = st.file_uploader("Choose 1 or more files", type=["pdf"], accept_multiple_files=True)
        if uploaded_file:
            merger = PdfMerger()
            for file in uploaded_file:
                merger.append(file)
            merged_file = "merged_all_files.pdf"
            merger.write(merged_file)
            merger.close()

            file_upload = client.files.upload(file=merged_file)
            chat2b = client.chats.create(model=MODEL_ID,
                history=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=file_upload.uri,
                                mime_type=file_upload.mime_type),
                        ]
                    ),
                ]                
            )
            prompt = st.chat_input("Enter your question here")
            if prompt:
                with st.chat_message("user"):
                    st.write(prompt)
                response = chat2b.send_message(prompt)
                with st.chat_message("model", avatar="🧞‍♀️"):
                    st.markdown(response.text)
    
    elif choice == "Upload Image/Gambar":
        st.subheader("Kamu bisa masukkan gambar😊")
        uploaded_file = st.file_uploader("Choose your PNG or JPEG file", type=['png', 'jpg', 'webp', 'jpeg'], accept_multiple_files=False)
        if uploaded_file:
            temp_image_path = upload_temp_file(uploaded_file, f"temp_uploaded_image.{uploaded_file.name.split('.')[-1]}")
            file_upload = client.files.upload(file=temp_image_path)
            chat3 = client.chats.create(model=MODEL_ID,
                history=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=file_upload.uri,
                                mime_type=file_upload.mime_type)
                        ]
                    )
                ]                               
            )
            prompt = st.chat_input("Enter your question here")
            if prompt:
                with st.chat_message("user"):
                    st.write(prompt)
                response = chat3.send_message(prompt)
                with st.chat_message("model", avatar="🧞‍♀️"):
                    st.markdown(response.text)
    
    elif choice == "Upload Audio/mp3":
        st.subheader("Upload Audio Kamu Disini😊")
        uploaded_file = st.file_uploader("Choose your mp3 or wav file", type=['mp3','wav'], accept_multiple_files=False)
        if uploaded_file:
            temp_audio_path = upload_temp_file(uploaded_file, f"temp_uploaded_audio.{uploaded_file.name.split('.')[-1]}")
            file_upload = client.files.upload(file=temp_audio_path)
            chat4 = client.chats.create(model=MODEL_ID,
                history=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=file_upload.uri,
                                mime_type=file_upload.mime_type),
                        ]
                    ),
                ]
            )
            prompt = st.chat_input("Enter your question here")
            if prompt:
                with st.chat_message("user"):
                    st.write(prompt)
                response = chat4.send_message(prompt)
                with st.chat_message("model", avatar="🧞‍♀️"):
                    st.markdown(response.text)
    
    elif choice == "Upload Video/mp4":
        st.subheader("Upload Video Kamu Disini😊")
        uploaded_file = st.file_uploader("Choose your mp4 or mov file", type=["mp4", "mov"], accept_multiple_files=False)
        if uploaded_file:
            temp_video_path = upload_temp_file(uploaded_file, f"temp_uploaded_video.{uploaded_file.name.split('.')[-1]}")
            video_file = client.files.upload(file=temp_video_path)
            while video_file.state == "PROCESSING":
                time.sleep(10)
                video_file = client.files.get(name=video_file.name)

            if video_file.state == "FAILED":
                raise ValueError("Proses Video Gagal")
            
            chat5 = client.chats.create(model=MODEL_ID,
                history=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=video_file.uri,
                                mime_type=video_file.mime_type),
                        ]
                    ),
                ]
            )
            prompt = st.chat_input("Enter your question here")
            if prompt:
                with st.chat_message("user"):
                    st.write(prompt)
                response = chat5.send_message(prompt)
                with st.chat_message("model", avatar="🧞‍♀️"):
                    st.markdown(response.text)

if __name__ == "__main__":
    setup_app()
    main()






