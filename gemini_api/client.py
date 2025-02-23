import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
gemini_api = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api)

def generate_expenses_description(statement_type, initial_data, final_data, accounts):
    """
    Elabora o resumo financeiro do mês.
    """
    message = ''' Elabore um resumo sobre a(s) {} entre os dias {} e {}, nas contas ({}), com no máximo, caracteres.
    Forneça mais detalhes técnicos. Aborde uma linguagem mais simples.
    Pule uma linha a cada 10 palavras.'''
    message = message.format(statement_type, initial_data, final_data, accounts)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content( message, generation_config = genai.GenerationConfig( max_output_tokens=300, ) )
    return response.text