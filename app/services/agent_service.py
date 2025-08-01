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
from app.db import vector_db, metadata_db
from app.services import notification


# Document Search Tool
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

# BOOKING TOOL
class InterviewBookingInput(BaseModel):
    full_name: str = Field(description="The full name of the person.")
    email: str = Field(description="The email address of the person.")
    date: str = Field(description="The requested date for the interview, e.g., '2024-09-15'.")
    time: str = Field(description="The requested time for the interview in 24-hour format, e.g., '14:30'.")

class InterviewBookingTool(BaseTool):
    name: str = "interview_booking_tool"
    description: str = "Use this tool to book an interview. It requires the person's full name, email, and the desired date and time."
    args_schema: Type[BaseModel] = InterviewBookingInput

    def _run(self, full_name: str, email: str, date: str, time: str) -> str:
        try:
            # Use a context manager to get a DB session
            db_session_gen = metadata_db.get_db()
            db = next(db_session_gen)
            
            # Save to DB
            booking_id = metadata_db.save_booking(db, full_name, email, date, time)
            
            # Send confirmation email
            notification.send_booking_confirmation(full_name, email, date, time)
            
            return f"Successfully booked interview for {full_name}. A confirmation email has been sent. The booking ID is {booking_id}."
        except Exception as e:
            return f"Error: Failed to book interview. Reason: {e}"
        finally:
            db.close()


# THE AGENT
def create_agent_executor():
    # ADDING TOOL TO THE LIST
    tools = [DocumentSearchTool(), InterviewBookingTool()] 
    
    # THE SYSTEM PROMPT
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant named PalmBot. You have two primary functions:
1.  Answer questions based on documents provided by the user.
2.  Book job interviews for candidates.

- To answer questions, **ALWAYS** use the `document_search` tool. Before calling the tool, use the chat history to rephrase follow-up questions into a standalone question.
- To book an interview, use the `interview_booking_tool`. You **MUST** have the person's full name, email, date, and time before using this tool. If any information is missing, you must ask the user for it.
- If the user asks a general greeting, respond conversationally."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=settings.GOOGLE_API_KEY)
    
    agent = create_tool_calling_agent(llm, tools, prompt)
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