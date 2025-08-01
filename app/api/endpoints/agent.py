from fastapi import APIRouter, HTTPException
from app.schemas.agent import ChatRequest, ChatResponse
from app.services import agent_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest):
    """
    This endpoint receives a user query and returns the agent's response.
    """
    if not request.query or not request.session_id:
        raise HTTPException(status_code=400, detail="Query and session_id are required.")

    # Call our agent service to get a response
    response_text = agent_service.run_chat(request.session_id, request.query)
    
    return ChatResponse(response=response_text, session_id=request.session_id)