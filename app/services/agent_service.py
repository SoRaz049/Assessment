from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.core.config import settings
from app.db import vector_db

# Define the Tools
@tool
def document_search(query: str) -> str:
    """
    Searches and returns relevant information from the uploaded documents 
    based on the user's query. Use this to answer questions about the documents.
    """
    print(f"Executing document search for query: '{query}'")
    # Get a retriever from our vector_db module. A retriever is a generic
    # interface for fetching documents.
    retriever = vector_db.get_retriever()
    
    # The 'invoke' method runs the search and returns a list of Document objects.
    results = retriever.invoke(query)
    
    # We format the results into a single string for the LLM.
    # We join the page_content of each retrieved document.
    return "\n---\n".join([doc.page_content for doc in results])


# Create the Agent
def create_agent_executor():
    """Creates the LangChain agent and the executor that runs it."""
    
    # Define the tools the agent can use. For now, it's just one.
    tools = [document_search]
    
    # Create the prompt template. This is the agent's "brain" and instructions.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant named PalmBot. You must use the 'document_search' tool to answer questions about the provided documents."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"), # This is where the agent does its "thinking"
    ])

    # Initialize the LLM. We are using Gemini Pro.
    # The `convert_system_message_to_human=True` is a specific requirement for some older Gemini models.
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest", 
        google_api_key=settings.GOOGLE_API_KEY, 
        temperature=0, 
        convert_system_message_to_human=True
    )
    
    # Create the agent itself by combining the LLM, the tools, and the prompt.
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the Agent Executor, which is the runtime for the agent.
    # `verbose=True` will print the agent's thought process to the console, which is great for debugging.
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

# Create the agent executor when the module is loaded
agent_executor = create_agent_executor()


#Define the main function to run the chat
def run_chat(query: str):
    """
    Runs the agent with a given query and returns the response.
    We will add session_id and memory later.
    """
    # The 'invoke' method runs the agent chain.
    response = agent_executor.invoke({"input": query})
    return response["output"]
