import streamlit as st
import streamlit.components.v1 as components
import json
import os
from PIL import Image
from google.genai import errors as genai_errors
from streamlit_oauth import OAuth2Component
from src.vision import extract_text_from_images
from src.parser import parse_text_to_tasks
from src.calendar_api import add_event_to_calendar
from src.config import GOOGLE_CREDENTIALS_PATH

# --- CONFIGURAÇÃO OAUTH ---
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Carrega credenciais do cliente
with open(GOOGLE_CREDENTIALS_PATH, "r") as f:
    client_config = json.load(f)
    # Suporte tanto para o formato 'web' quanto 'installed' do JSON do Google
    key = "web" if "web" in client_config else "installed"
    CLIENT_ID = client_config[key]["client_id"]
    CLIENT_SECRET = client_config[key]["client_secret"]

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL)

st.set_page_config(page_title="Notes to Calendar", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap');
        
        html, body, .stApp {
            font-family: 'Geist', sans-serif !important;
        }
        
        p, h1, h2, h3, h4, h5, h6 {
            font-family: 'Geist', sans-serif !important;
        }

        .stButton button, .stTextInput input, .stTextArea textarea {
            font-family: 'Geist', sans-serif !important;
        }

        .stMarkdown span, .stText span, .stAlert span {
            font-family: 'Geist', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

if "parsed_tasks" not in st.session_state:
    st.session_state.parsed_tasks = None
if "is_completed" not in st.session_state:
    st.session_state.is_completed = False
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- SIDEBAR (Gestão de Conta) ---
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/calendar_2020q4_48dp.png", width=50)
    st.title("Configurações")
    st.divider()
    
    st.subheader("CONTA GOOGLE")
    
    # Define o caminho do token
    base_dir = os.path.dirname(os.path.abspath(GOOGLE_CREDENTIALS_PATH))
    token_path = os.path.join(base_dir, 'token.json')
    
    # Verifica se já temos um token (no arquivo ou na sessão)
    if "auth_token" not in st.session_state and os.path.exists(token_path):
        with open(token_path, "r") as f:
            st.session_state.auth_token = json.load(f)

    if "auth_token" in st.session_state:
        st.success("🟢 Conectado ao Google Calendar")
        if st.button("🔴 Sair / Trocar Conta", help="Remove as credenciais salvas"):
            if os.path.exists(token_path): os.remove(token_path)
            del st.session_state.auth_token
            st.toast("Credenciais removidas!")
            st.rerun()
    else:
        st.error("🔴 Não conectado")
        result = oauth2.authorize_button(
            name="Login com Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri="http://localhost:8501", # Ajustar se necessário para o ambiente real
            scope=" ".join(SCOPES),
            key="google_login",
            use_container_width=True,
            height=700,
        )

        if result:
            st.session_state.auth_token = result.get("token")
            # Injeta client_id e client_secret no dicionário do token para compatibilidade com google-auth
            st.session_state.auth_token["client_id"] = CLIENT_ID
            st.session_state.auth_token["client_secret"] = CLIENT_SECRET
            
            with open(token_path, "w") as f:
                json.dump(st.session_state.auth_token, f)
            st.rerun()

    st.divider()
    st.caption("AI Notes to Calendar v1.1")
    st.caption("Desenvolvido com Streamlit + Gemini")

st.title("Upload de Anotações para a Agenda")
st.write("Faça o upload de uma ou mais imagens com as suas anotações para processarmos e adicionarmos à sua agenda.")

def reset_app():
    old_key = st.session_state.uploader_key
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.uploader_key = old_key + 1
    st.rerun()

uploaded_files = st.file_uploader(
    "Escolha as imagens", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True, 
    key=f"uploader_{st.session_state.uploader_key}"
)

def display_uploaded_images(images):
    if len(images) > 1:
        tabs = st.tabs([f"📄 Imagem {i+1}" for i in range(len(images))])
        for i, tab in enumerate(tabs):
            tab.image(images[i], width="stretch")
    else:
        st.image(images[0], width="stretch")

if uploaded_files:
    images = [Image.open(f) for f in uploaded_files]
    
    if st.session_state.parsed_tasks or st.session_state.is_completed:
        with st.expander("🖼️ Ver as imagens enviadas (Oculto para economizar espaço)", expanded=False):
            display_uploaded_images(images)
    else:
        display_uploaded_images(images)
        if st.button("Processar Imagens", type="primary", width="stretch"):
            try:
                with st.spinner("🔍 Analisando caligrafia e extraindo texto..."):
                    raw_text = extract_text_from_images(images)
                
                with st.spinner("✅ Texto extraído! Organizando tarefas e datas..."):
                    json_tasks = parse_text_to_tasks(raw_text)
                
                st.session_state.parsed_tasks = json_tasks
                st.session_state.raw_text = raw_text
                st.session_state.scroll_to_tasks = True
                st.session_state.is_completed = False
                
                st.toast("✅ Processamento concluído!")
                st.rerun()
            except genai_errors.ClientError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.error("🚨 Limite de cota atingido! O Google Gemini (IA) recebeu muitas requisições. Aguarde um minuto e tente novamente.")
                else:
                    st.error(f"Erro na IA do Google: {e}")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")

if st.session_state.is_completed:
    st.success("🎉 Tudo certo! Sua agenda foi atualizada com os novos eventos.")
    st.balloons()
    if st.button("🔄 Processar Nova Anotação", type="primary", width="stretch"):
        reset_app()
        
elif st.session_state.parsed_tasks:
    st.success("Mágica realizada com sucesso! Verifique os dados abaixo e adicione à agenda.")
    
    with st.expander("Ver transcrição original", expanded=False):
        st.text_area("Resultado", st.session_state.raw_text, height=150, label_visibility="collapsed", disabled=True)
    
    st.markdown("<div id='scroll-target-tasks'></div>", unsafe_allow_html=True)
    st.subheader("Lista de Tarefas (Editável):")
    
    current_tasks = st.session_state.parsed_tasks.get('tasks', [])
    
    if not current_tasks:
        st.warning("⚠️ Nenhuma tarefa clara descrita na imagem foi identificada. Você pode adicioná-las manualmente.")
        
    edited_tasks = st.data_editor(
        current_tasks,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "title": st.column_config.TextColumn("📝 Título", required=True),
            "description": st.column_config.TextColumn("ℹ️ Descrição"),
            "date": st.column_config.DateColumn("📅 Data", format="DD/MM/YYYY", help="Selecione a data do compromisso."),
            "time": st.column_config.TimeColumn("⏰ Hora", format="HH:mm", help="Defina o horário (opcional)."),
        }
    )
    
    st.session_state.parsed_tasks['tasks'] = edited_tasks
    st.divider()
    
    st.subheader("Finalizar Agendamento")
    
    if "auth_token" not in st.session_state:
        st.warning("⚠️ Você precisa se conectar ao Google para agendar as tarefas.")
        result_main = oauth2.authorize_button(
            name="Conectar ao Google Calendar",
            icon="https://www.google.com/favicon.ico",
            redirect_uri="http://localhost:8501",
            scope=" ".join(SCOPES),
            key="google_login_main",
            use_container_width=True,
            height=700,
        )

        if result_main:
            st.session_state.auth_token = result_main.get("token")
            # Injeta client_id e client_secret para compatibilidade com google-auth
            st.session_state.auth_token["client_id"] = CLIENT_ID
            st.session_state.auth_token["client_secret"] = CLIENT_SECRET
            
            # Salva no token.json para persistência
            base_dir = os.path.dirname(os.path.abspath(GOOGLE_CREDENTIALS_PATH))
            token_path = os.path.join(base_dir, 'token.json')
            with open(token_path, "w") as f:
                json.dump(st.session_state.auth_token, f)
            st.rerun()
    else:
        st.info("💡 As tarefas acima serão enviadas para o seu Google Calendar principal.", icon="📅")
        
        if st.button("Adicionar Todas as Tarefas à Agenda 🗓️", type="primary", width="stretch"):
            tasks_to_add = st.session_state.parsed_tasks.get('tasks', [])
        
            if not tasks_to_add:
                 st.warning("Nenhuma tarefa para enviar!")
            else:
                success_count = 0
                progress_text = st.empty()
                
                for task in tasks_to_add:
                    with st.spinner(f"⏳ Agendando: {task.get('title')}..."):
                        event_link = add_event_to_calendar(task)
                        if event_link:
                            st.toast(f"✅ Tarefa '{task.get('title')}' agendada!")
                            success_count += 1
                        else:
                            st.toast(f"❌ Erro ao adicionar '{task.get('title')}'")
                
                if success_count > 0:
                    st.session_state.is_completed = True
                    st.toast(f"🎉 Sucesso! {success_count} eventos criados.")
                    st.rerun()

if st.session_state.get("scroll_to_tasks", False):
    components.html('''
    <script>
        var doc = window.parent.document;
        var target = doc.getElementById('scroll-target-tasks');
        if (target) {
            target.scrollIntoView({behavior: 'smooth', block: 'start'});
            
            if (!doc.getElementById('pulse-style')) {
                var style = doc.createElement('style');
                style.id = 'pulse-style';
                style.innerHTML = `
                @keyframes highlightPulse {
                    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.5); background-color: rgba(99, 102, 241, 0.15); }
                    50% { box-shadow: 0 0 0 15px rgba(99, 102, 241, 0); background-color: rgba(99, 102, 241, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
                }
                .pulse-anim { animation: highlightPulse 1.8s ease-out; border-radius: 8px; }
                `;
                doc.head.appendChild(style);
            }
            
            setTimeout(() => {
                var elements = Array.from(doc.querySelectorAll('h3'));
                var header = elements.find(el => el.textContent.includes('Lista de Tarefas'));
                if (header) {
                    header.classList.add('pulse-anim');
                    setTimeout(() => header.classList.remove('pulse-anim'), 2000);
                }
                
                var tableContainer = doc.querySelector('[data-testid="stDataFrame"]');
                if (tableContainer) {
                    tableContainer.classList.add('pulse-anim');
                    setTimeout(() => tableContainer.classList.remove('pulse-anim'), 2000);
                }
            }, 600);
        }
    </script>
    ''', height=0)
    st.session_state.scroll_to_tasks = False
