# Actionable Items , Decision , Questions

import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough , RunnableLambda

def get_llm():
    return ChatMistralAI(model='mistral-small-latest',mistral_api_key=os.getenv("MISTRAL_API_KEY"),temperature=0.2)

def build_chain(system_prompt : str):
    llm = get_llm()
    return (
        RunnablePassthrough() | RunnableLambda(lambda x: {'text' : x}) | 
        ChatPromptTemplate.from_messages([
            ('system', system_prompt),
            ('human','{text}')
        ]) | llm | StrOutputParser()
    )

def extract_action_items(transcript:str)->str:
    chain = build_chain(
        'You are an expert meeting analyst. From the meeting transcript,'
        'extract all action items .for each provide \n'
        '- Task Description\n'
        '- Owner (who is responsible)\n'
        "- Deadline (if mentioned , else write 'Not Specified')\n\n"
        "format as a numbered list. if none found say 'No action items found'."
    )

    return chain.invoke(transcript)

# if transcript is long, you needed create Chunking
def extract_key_decisions(transcript:str)->str:
    chain = build_chain(
        'You are an expert meeting analyst. From the meeting transcript'
        'extract all key decision made. Format as a numbered list.'
        "if none found say 'No key decision found'"
    )

    return chain.invoke(transcript)

def extract_questions(transcript:str)->str:
    chain = build_chain(
        'From the meeting transcript , extract all unresolved questions'
        'or topic needs follow up. Follow as a numbered list'
        "If none found say 'No open Question found'"
    )

    return chain.invoke(transcript)

