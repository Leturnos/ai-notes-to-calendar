import json
from datetime import datetime
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from src.config import GEMINI_API_KEY

class Task(BaseModel):
    title: str = Field(description="Título breve e claro da tarefa ou compromisso")
    description: Optional[str] = Field(None, description="Detalhes adicionais ou contexto, se houver")
    date: Optional[str] = Field(None, description="Data da tarefa no formato YYYY-MM-DD, se mencionada de alguma forma")
    time: Optional[str] = Field(None, description="Horário da tarefa no formato HH:MM (24 horas), se mencionado")

class TasksResponse(BaseModel):
    tasks: List[Task]

def parse_text_to_tasks(raw_text: str) -> dict:
    """
    Recebe o texto bruto extraído da imagem e utiliza o Gemini
    para estruturar numa lista de tarefas, retornando um JSON nativo.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Data atual para que referências como "amanhã" e "hoje" façam sentido no parsing
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    Abaixo está o texto bruto da transcrição de uma anotação visual.
    Aja como um assistente especialista de produtividade. 
    Analise a transcrição linha por linha e extraia todas as pendências, tarefas ou compromissos. 
    Estruture de forma padronizada.
    
    INSTRUÇÕES IMPORTANTES:
    - Considere a data atual do usuário sendo: {current_date}. 
    - Deduzir as datas relativas (ex: "amanhã", "nesta sexta") com base no dia de hoje.
    - Se a tarefa não possuir uma data especificada ou dedutível, deixe o campo 'date' vazio/nulo.
    - Se a tarefa não tiver hora detalhada, deixe o campo 'time' vazio/nulo.
    
    TEXTO DA TRANSCRIÇÃO:
    {raw_text}
    """
    
    # Geração do conteúdo estruturada em JSON por schema
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TasksResponse,
            temperature=0.1
        )
    )
    
    # Transforma e retorna o JSON
    try:
        return json.loads(response.text)
    except Exception as e:
        print(f"Erro ao converter retorno para dicionário do Python: {e}")
        return {"tasks": []}
