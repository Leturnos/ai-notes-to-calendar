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
    
    # Botão básico para processar
    if st.button("Processar Imagem"):
        with st.spinner("Extraindo texto e processando tarefas..."):
            try:
                # 1. Visão: Transcreve o texto da anotação
                texto_bruto = extract_text_from_image(image)
                
                # 2. Parser: Transforma o texto bruto para JSON (Lista de Tarefas)
                json_tarefas = parse_text_to_tasks(texto_bruto)
                
                # Salvando o resultado para liberar o próximo botão da interface
                st.session_state.tarefas_parseadas = json_tarefas
                st.session_state.texto_bruto = texto_bruto
                
                st.success("Mágica realizada com sucesso! Verifique os dados abaixo e adicione à agenda.")
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")

# Renderização do Resultado (ocorre independente se processou agora ou estava em cache)
if st.session_state.tarefas_parseadas:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Transcrição:")
        st.text_area("Resultado", st.session_state.texto_bruto, height=300, label_visibility="collapsed")
    
    with col2:
        st.subheader("JSON de Tarefas:")
        st.json(st.session_state.tarefas_parseadas)

    st.divider()
    
    
