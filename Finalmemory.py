
from pydantic import BaseModel
from langchain.agents import tool
from answeringmemory import Response
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

tools = [get_history,get_instruction]

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

    from langchain.prompts import ChatPromptTemplate
    from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
    from langchain.prompts import MessagesPlaceholder
    prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful but sassy assistant"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    from langchain.memory import ConversationBufferMemory
    memory = ConversationBufferMemory(return_messages=True,memory_key="chat_history")
    chain = prompt | model | OpenAIFunctionsAgentOutputParser()
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.agents.format_scratchpad import format_to_openai_functions
    agent_chain = RunnablePassthrough.assign(agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])) | chain
    from langchain.agents import AgentExecutor
    agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=False,memory=memory)

    return agent_executor
    result1 = agent_executor.invoke({"input": "Hello my name is Nguyên"})
    print(result1["output"])
    result2 = agent_executor.invoke({"input": "What is my name?"})
    print(result2["output"])
    
    return "done"
if __name__ =="__main__":
   result = function_calling("hjkgkjs")
   print(result.invoke({"input": "Làm thế nào để sửa lỗi int3170 trên máy CNC1?"})["output"])
   print(result.invoke({"input": "Bạn chắc không?"})["output"])