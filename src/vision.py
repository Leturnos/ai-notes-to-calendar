from google import genai
from PIL import Image
from src.config import GEMINI_API_KEY

def extract_text_from_images(images: list[Image.Image]) -> str:
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
    
    return response.text
