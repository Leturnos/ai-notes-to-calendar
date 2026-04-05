import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from src.vision import extract_text_from_images
from src.parser import parse_text_to_tasks
from src.calendar_api import add_event_to_calendar

st.set_page_config(page_title="Notes to Calendar", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap');
        html, body, [class*="st-"], .stApp, p, span, h1, h2, h3, div {
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

if uploaded_files:
    images = [Image.open(f) for f in uploaded_files]
    
    if st.session_state.parsed_tasks or st.session_state.is_completed:
        with st.expander("🖼️ Ver as imagens enviadas (Oculto para economizar espaço)", expanded=False):
            st.image(images, caption=[f"Imagem {i+1}" for i in range(len(images))], width="stretch")
    else:
        st.image(images, caption=[f"Imagem {i+1}" for i in range(len(images))], width="stretch")
        if st.button("Processar Imagens", type="primary", use_container_width=True):
            with st.spinner("Extraindo texto e processando tarefas..."):
                try:
                    raw_text = extract_text_from_images(images)
                    json_tasks = parse_text_to_tasks(raw_text)
                    
                    st.session_state.parsed_tasks = json_tasks
                    st.session_state.raw_text = raw_text
                    st.session_state.scroll_to_tasks = True
                    st.session_state.is_completed = False
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")

if st.session_state.is_completed:
    st.success("🎉 Tudo certo! Sua agenda foi atualizada com os novos eventos.")
    st.balloons()
    if st.button("🔄 Processar Nova Anotação", type="primary", use_container_width=True):
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
        use_container_width=True,
        column_config={
            "title": st.column_config.TextColumn("Título", required=True),
            "description": st.column_config.TextColumn("Descrição"),
            "date": st.column_config.DateColumn("Data", format="YYYY-MM-DD", help="Escreva a data ou use o calendário (YYYY-MM-DD)."),
            "time": st.column_config.TimeColumn("Hora", format="HH:mm:ss", help="Escreva a hora, ex: 14:00"),
        }
    )
    
    st.session_state.parsed_tasks['tasks'] = edited_tasks
    st.divider()
    
    st.subheader("Ações Finais")
    st.info("Ao clicar no botão abaixo, iremos autenticar no Google. Caso seja seu primeiro acesso, uma página de login abrirá automaticamente.", icon="💡")
    
    if st.button("Adicionar Todas as Tarefas à Agenda 🗓️", type="primary", use_container_width=True):
        with st.spinner("Autenticando e gerando eventos no Google Calendar..."):
            tasks_to_add = st.session_state.parsed_tasks.get('tasks', [])
            
            if not tasks_to_add:
                 st.warning("Nenhuma tarefa para enviar!")
            else:
                success_count = 0
                for task in tasks_to_add:
                    event_link = add_event_to_calendar(task)
                    if event_link:
                        st.toast(f"✅ Tarefa '{task.get('title')}' agendada!")
                        success_count += 1
                    else:
                        st.toast(f"❌ Erro ao adicionar '{task.get('title')}'")
                
                if success_count > 0:
                    st.session_state.is_completed = True
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
