"""
WebSocket endpoints for real-time chat.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and store connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, user_id: int):
        """Remove connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user."""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time conversation."""
    await manager.connect(websocket, user_id)
    
    # Import here to avoid circular imports
    from agents.conversation import ConversationPartnerAgent
    
    conversation_agent = ConversationPartnerAgent()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_message = data.get("message")
            level = data.get("level", "B1")
            topic = data.get("topic", "general")
            
            if not user_message:
                await manager.send_personal_message({
                    "error": "Message is required"
                }, user_id)
                continue
            
            logger.info(f"Received from user {user_id}: {user_message}")
            
            # Process with conversation agent
            try:
                response = await conversation_agent.chat(
                    user_message=user_message,
                    context={
                        "level": level,
                        "topic": topic,
                        "user_id": user_id
                    }
                )
                
                # Send response back
                await manager.send_personal_message({
                    "reply": response.get("reply"),
                    "corrections": response.get("corrections", []),
                    "new_vocabulary": response.get("new_vocabulary", []),
                    "engagement_score": response.get("engagement_score", 0)
                }, user_id)
                
                logger.info(f"Sent reply to user {user_id}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await manager.send_personal_message({
                    "error": "Failed to process message",
                    "detail": str(e)
                }, user_id)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"User {user_id} disconnected from chat")
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
        manager.disconnect(user_id)


@router.websocket("/ws/evaluation/{user_id}")
async def websocket_evaluation(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for interactive evaluation."""
    await websocket.accept()
    
    from agents.evaluator import EvaluatorAgent
    
    evaluator = EvaluatorAgent()
    
    try:
        # Initialize evaluation state
        state = {
            "messages": [],
            "student_level": None,
            "strengths": [],
            "weaknesses": [],
            "conversation_history": [],
            "question_count": 0
        }
        
        # Start evaluation loop
        while state["question_count"] < 7 and not state.get("student_level"):
            # Get next question
            state = await evaluator.ask_question(state)
            
            # Send question to client
            last_message = state["messages"][-1]
            await websocket.send_json({
                "type": "question",
                "content": last_message.get("content"),
                "question_number": state["question_count"]
            })
            
            # Wait for student response
            data = await websocket.receive_json()
            user_response = data.get("message")
            
            if not user_response:
                continue
            
            # Add response to state
            state["messages"].append({
                "role": "user",
                "content": user_response
            })
            
            # Analyze response
            state = await evaluator.analyze_response(state)
            
            # Check if should continue
            if evaluator.should_continue(state) == "finish":
                break
        
        # Determine final level
        final_state = await evaluator.determine_level(state)
        
        # Send final assessment
        await websocket.send_json({
            "type": "assessment_complete",
            "level": final_state.get("student_level"),
            "assessment": final_state.get("final_assessment"),
            "strengths": final_state.get("strengths", []),
            "weaknesses": final_state.get("weaknesses", [])
        })
        
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from evaluation")
    except Exception as e:
        logger.error(f"Evaluation WebSocket error: {e}", exc_info=True)
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()
