import streamlit as st
import streamlit as st
import tempfile
from gtts import gTTS
import base64
from utils import PDFSummarizer

# Função para limpar o estado do carregamento do arquivo e resetar a barra de progresso
def clear_uploaded_file():
    st.session_state.uploaded_file = None
    st.session_state.progress = 0

# Função para converter texto em áudio e gerar link de download
def text_to_audio(text, lang='pt'):
    tts = gTTS(text, lang=lang)
    tts.save("summary.mp3")
    audio_file = open("summary.mp3", "rb")
    audio_bytes = audio_file.read()
    audio_file.close()
    return audio_bytes

# Função para gerar o link de download do arquivo de áudio
def get_audio_download_link(audio_bytes, filename='summary.mp3'):
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Baixar áudio</a>'
    return href

# Adicionar código do Streamlit aqui
st.title("PDF Summarizer & Audio Converter")
st.write("""
Upload a PDF file and get a concise summary of its content. This application not only summarizes the text from your PDF documents but also converts the summary into audio, allowing you to listen to it on the go. Simplify your reading and make information more accessible with our PDF Summary and Audio Converter.
""")

# Solicitar chave da API OpenAI
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
if openai_api_key:
    uploaded_file = st.file_uploader("Upload the PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.write("File uploaded successfully!")

        # Salvar o arquivo carregado em um local temporário
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        summarizer = PDFSummarizer(file_path=temp_file_path, openai_api_key=openai_api_key)

        progress_bar = st.progress(0)

        def update_progress(progress):
            progress_bar.progress(progress)

        summary = summarizer.run(progress_callback=update_progress)
        st.write(summary)

        if st.button("Convert Summary to Audio"):
            # Converter o resumo em áudio
            audio_bytes = text_to_audio(summary)

            # Exibir o player de áudio no corpo principal
            st.audio(audio_bytes, format='audio/mp3')

            # Exibir o player de áudio na barra lateral
            st.sidebar.audio(audio_bytes, format='audio/mp3')

            # Link para baixar o áudio na barra lateral
            st.sidebar.markdown(get_audio_download_link(audio_bytes), unsafe_allow_html=True)

        # Botão para excluir o arquivo e limpar entradas
        if st.button("Delete File"):
            clear_uploaded_file()
            st.experimental_rerun()
    else:
        st.session_state.progress = 0
        progress_bar = st.progress(st.session_state.progress)
else:
    st.write("Please enter your OpenAI API Key to proceed.")
