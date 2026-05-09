from google import genai
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import GEMINI_API_KEY

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def extract_text_from_images(images: list[Image.Image]) -> str:
    """
    Extrai texto das imagens usando o modelo Gemini. 
    Inclui lógica de retry para falhas temporárias de conexão ou API.
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = (
            "Você é um especialista em ler anotações manuscritas (caligrafia difícil). "
            "Transcreva o texto da(s) imagem(ns) de forma inteligente: "
            "Use o contexto para deduzir corretamente as palavras, corrigindo distorções visuais "
            "e formando frases que façam sentido (ex: palavras como 'reformar box acrílico' em vez de letras truncadas). "
            "IMPORTANTE: Você tem PERMISSÃO para corrigir palavras pelo contexto, MAS É PROIBIDO "
            "alterar NÚMEROS (ex: se na imagem está 412, mantenha estritamente 412). "
            "Retorne APENAS o texto bruto da transcrição, sem adicionar comentários ou introduções."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt] + images
        )
        
        if not response.text:
            raise ValueError("O Gemini não retornou nenhum texto para as imagens fornecidas.")
            
        return response.text
    except Exception as e:
        # Re-levanta a exceção para que o @retry possa atuar nas tentativas
        # Nas outras exceções não-temporárias, o erro será capturado no app.py
        raise e
