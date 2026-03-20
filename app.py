import streamlit as st
from PIL import Image
from src.vision import extract_text_from_image

st.set_page_config(page_title="Notes to Calendar", layout="centered")

st.title("Upload de Anotações para a Agenda")
st.write("Faça o upload de uma imagem com as suas anotações para processarmos e adicionarmos à sua agenda.")

# Upload de imagem
uploaded_file = st.file_uploader("Escolha uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Exibição da imagem
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", width="stretch")
    
    # Botão básico
    if st.button("Processar Imagem"):
        with st.spinner("Extraindo texto da imagem com Inteligência Artificial..."):
            try:
                texto_bruto = extract_text_from_image(image)
                st.success("Texto extraído com sucesso!")
                st.subheader("Retorno Bruto da IA:")
                st.text_area("Resultado", texto_bruto, height=250)
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
