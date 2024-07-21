import streamlit as st
from utils import PDFSummarizer
import tempfile
from gtts import gTTS
import base64


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

# Add Streamlit code here
st.title("RESUMIDOR DE PDF")
st.write("Faça o upload de um arquivo PDF e obtenha um resumo do conteúdo:")

uploaded_file = st.file_uploader("Carregue o arquivo", type=["pdf"])

if uploaded_file is not None:
    st.write("Arquivo carregado com sucesso!")
    
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
    
    summarizer = PDFSummarizer(temp_file_path)
    
    progress_bar = st.progress(0)
    
    def update_progress(progress):
        progress_bar.progress(progress)

    summary = summarizer.run(progress_callback=update_progress)
    st.write(summary)

    # Converter o resumo em áudio
    audio_bytes = text_to_audio(summary)

    # Exibir o player de áudio
    st.audio(audio_bytes, format='audio/mp3')

    # Link para baixar o áudio
    st.markdown(get_audio_download_link(audio_bytes), unsafe_allow_html=True)
    
    # Botão para excluir o arquivo e limpar entradas
    if st.button("Excluir Arquivo"):
        clear_uploaded_file()
        st.experimental_rerun()
else:
    st.session_state.progress = 0
    progress_bar = st.progress(st.session_state.progress)
