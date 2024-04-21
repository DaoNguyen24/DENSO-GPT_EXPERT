
from pydantic import BaseModel
from langchain.agents import tool
from answering import Response
from history_retrive import retrive_history
from langchain.chat_models import ChatOpenAI
import openai


@tool
def get_history(query:str)-> str:
 """Search for history of a machine"""
 return retrive_history(query=query)

@tool
def get_instruction(query:str)->str:
    """Use when you want to solve for a problem of a machine"""
    return Response(query=query)

from langchain.schema.agent import AgentFinish
def route(result):
    if isinstance(result, AgentFinish):
        return result.return_values['output'],''
    else:
        tools = {
            "get_instruction": get_instruction, 
            "get_history": get_history,
        }
        print (result.tool_input)
        return tools[result.tool].run(result.tool_input)

def function_calling(query):
    from langchain.tools.render import format_tool_to_openai_function
    functions = [
        format_tool_to_openai_function(f) for f in [
            get_history, get_instruction
        ]
    ]
    model = ChatOpenAI(model="gpt-3.5-turbo",temperature=0,openai_api_key='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').bind(functions=functions)
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
    from langchain.memory import ConversationBufferMemory
    from operator import itemgetter
    memory = ConversationBufferMemory(return_messages=True)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are helpful but sassy assistant"),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}"),
    ])
    chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))|prompt | model | OpenAIFunctionsAgentOutputParser()|route)

    #result,metadata = chain.invoke({"input": query})
    result,metadata = chain.invoke({"input": "My name is Nguyen"})
    print(result)
    print(metadata)
    result,metadata = chain.invoke({"input": "What is my name?"})
    print(result)
    print(metadata)

if __name__ =="__main__":
   function_calling("Cho tôi lịch sử máy Shot last ")

