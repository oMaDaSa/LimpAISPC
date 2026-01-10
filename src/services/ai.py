'''
# Temporariamente desabilitado - aguardando layer correta
from langchain_aws import ChatBedrock
from core.config import BEDROCK_CONFIG, PROMPT_TEMPLATE

def ai_response(user_input: str):
    try:
        llm = ChatBedrock(
            model_id=BEDROCK_CONFIG["model_id"],
            region_name=BEDROCK_CONFIG["region_name"],
            credentials_profile_name=None, 
            model_kwargs=BEDROCK_CONFIG["model_kwargs"]
        )
        prompt = PROMPT_TEMPLATE.format(question=user_input)
        
        response = llm.invoke(prompt)
        
        return response.content
        
    except Exception as e:
        raise Exception(f"Erro ao processar resposta da IA: {str(e)}")
'''