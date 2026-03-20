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
        "Por favor, transcreva e extraia todo o texto e informações contidas "
        "nesta imagem, de forma exata e como estão estruturadas. "
        "Retorne APENAS o texto bruto da sua transcrição, sem adicionar outros comentários."
    )
    
    # Chamada para a API usando o novo padrão (recomendando gemini-2.5-flash)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, image]
    )
    
    return response.text
