import streamlit as st
from PIL import Image
from src.vision import extract_text_from_image
from src.parser import parse_text_to_tasks

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
        with st.spinner("Extraindo texto e processando tarefas..."):
            try:
                # 1. Visão: Transcreve o texto da anotação
                texto_bruto = extract_text_from_image(image)
                
                # 2. Parser: Transforma o texto bruto para JSON (Lista de Tarefas)
                json_tarefas = parse_text_to_tasks(texto_bruto)
                
                st.success("Mágica realizada com sucesso!")
                
                # Layout e Visualização (Coluna 1: Texto Bruto | Coluna 2: JSON)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Transcrição:")
                    st.text_area("Resultado", texto_bruto, height=300, label_visibility="collapsed")
                
                with col2:
                    st.subheader("JSON de Tarefas:")
                    st.json(json_tarefas)
                    
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
