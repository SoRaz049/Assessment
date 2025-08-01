from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from typing import Type
from langchain_core.runnables import RunnablePassthrough

from app.core.config import settings
from app.db import vector_db

# The Tool
class DocumentSearchInput(BaseModel):
    query: str = Field(description="The user's question to search for in the documents.")

class DocumentSearchTool(BaseTool):
    name: str = "document_search"
    description: str = "Use this to answer questions about the provided documents. This is the only way to get information from the documents."
    args_schema: Type[BaseModel] = DocumentSearchInput

    def _run(self, query: str) -> str:
        print(f"Tool running with query: '{query}'")
        retriever = vector_db.get_retriever()
        results = retriever.invoke(query)
        
        if not results:
            return "No information found in the documents for that query."
        return "\n---\n".join([doc.page_content for doc in results])

# The Agent
def create_agent_executor():
    tools = [DocumentSearchTool()]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant named PalmBot. Your primary function is to answer questions based on a set of documents provided by the user.

- **ALWAYS** use the `document_search` tool to answer any user question about people, places, topics, or any other specific information.
- Before calling the tool, use the chat history to rephrase the user's follow-up questions into a standalone question. For example, if the user asks "Where are they located?" after a question about "QuantumLeap AI", you should call the tool with the query "Where is QuantumLeap AI located?".
- Do not use your own general knowledge to answer questions about the documents. If the information is not in the documents, say that you cannot find the answer in the provided context.
- If the user asks a general greeting like "hello" or "how are you", you can respond conversationally."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=settings.GOOGLE_API_KEY)
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # The AgentExecutor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # The memory wrapper 
    agent_with_memory = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: RedisChatMessageHistory(session_id, url=settings.REDIS_URL),
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    return agent_with_memory

agent_executor_with_memory = create_agent_executor()

def run_chat(session_id: str, query: str):
    config = {"configurable": {"session_id": session_id}}
    response = agent_executor_with_memory.invoke(
        {"input": query}, 
        config=config
    )
    return response["output"]