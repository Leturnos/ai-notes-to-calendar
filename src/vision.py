from google import genai
from PIL import Image
from src.config import GEMINI_API_KEY

def extract_text_from_image(image: Image.Image) -> str:
    """
    Recebe uma imagem (PIL Image), envia para o modelo Gemini
    e retorna o texto bruto extraído da imagem.
    """
    # Inicializando o cliente da nova versão do SDK
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = (
        "Você é um especialista em ler anotações manuscritas (caligrafia difícil). "
        "Transcreva o texto da imagem de forma inteligente: "
        "Use o contexto para deduzir corretamente as palavras, corrigindo distorções visuais "
        "e formando frases que façam sentido (ex: palavras como 'reformar box acrílico' em vez de letras truncadas). "
        "IMPORTANTE: Você tem PERMISSÃO para corrigir palavras pelo contexto, MAS É PROIBIDO "
        "alterar NÚMEROS (ex: se na imagem está 412, mantenha estritamente 412). "
        "Retorne APENAS o texto bruto da transcrição, sem adicionar comentários ou introduções."
    )
    
    # Chamada para a API usando o novo padrão (recomendando gemini-2.5-flash)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, image]
    )
    
    return response.text
