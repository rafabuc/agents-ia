"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self):
        """Test health check."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_docs_available(self):
        """Test that API docs are available."""
        response = client.get("/docs")
        assert response.status_code == 200


class TestEvaluationEndpoint:
    """Test evaluation endpoint."""
    
    def test_evaluate_user(self):
        """Test user evaluation."""
        response = client.post(
            "/api/v1/evaluate",
            json={
                "user_id": 1,
                "initial_message": "Hello, I want to learn English"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "level" in data
    
    def test_evaluate_missing_user_id(self):
        """Test evaluation without user_id."""
        response = client.post(
            "/api/v1/evaluate",
            json={"initial_message": "Hello"}
        )
        assert response.status_code == 422  # Validation error


class TestLessonEndpoints:
    """Test lesson endpoints."""
    
    def test_create_lesson(self):
        """Test lesson creation."""
        response = client.post(
            "/api/v1/lesson/create",
            json={
                "topic": "Present Perfect",
                "level": "B1"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "lesson" in data
        assert data["topic"] == "Present Perfect"
    
    def test_explain_grammar(self):
        """Test grammar explanation."""
        response = client.post(
            "/api/v1/lesson/explain",
            params={
                "concept": "Present Perfect",
                "level": "B1"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
    
    def test_get_examples(self):
        """Test getting examples."""
        response = client.post(
            "/api/v1/lesson/examples",
            params={
                "word_or_phrase": "get over",
                "context": "health"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data


class TestProgressEndpoint:
    """Test progress endpoint."""
    
    def test_get_progress(self):
        """Test getting user progress."""
        response = client.get("/api/v1/progress/1")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data


@pytest.mark.asyncio
class TestWebSocket:
    """Test WebSocket endpoints."""
    
    def test_websocket_chat(self):
        """Test WebSocket chat connection."""
        with client.websocket_connect("/ws/chat/1") as websocket:
            # Send message
            websocket.send_json({
                "message": "Hello!",
                "level": "B1",
                "topic": "greeting"
            })
            
            # Receive response
            data = websocket.receive_json()
            assert "reply" in data


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint."""
        response = client.get("/api/v1/invalid")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON in request."""
        response = client.post(
            "/api/v1/lesson/create",
            data="invalid json"
        )
        assert response.status_code == 422


class TestRateLimiting:
    """Test rate limiting (if implemented)."""
    
    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    def test_rate_limit(self):
        """Test rate limiting."""
        # Make many requests
        for _ in range(100):
            response = client.get("/health")
        
        # Should get rate limited
        response = client.get("/health")
        assert response.status_code == 429
