import streamlit as st
from PIL import Image

st.set_page_config(page_title="Notes to Calendar", layout="centered")

st.title("Upload de Anotações para a Agenda")
st.write("Faça o upload de uma imagem com as suas anotações para processarmos e adicionarmos à sua agenda.")

# Upload de imagem
uploaded_file = st.file_uploader("Escolha uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Exibição da imagem
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_container_width=True)
    
    # Botão básico
    if st.button("Processar Imagem"):
        st.info("Funcionalidade de processamento será implementada em breve!")
