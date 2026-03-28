from unittest.mock import patch
from datetime import datetime
from app.api.chat.schemas import ConversationResponse, MessageResponse


FIXED_TS = datetime(2024, 1, 1, 12, 0, 0)

CONVERSATIONS_URL = "/chat/conversations"
CONVERSATION_ID = "conv-1"
MESSAGE_ID = "msg-uuid"
CONVERSATION_URL = f"{CONVERSATIONS_URL}/{CONVERSATION_ID}"
MESSAGES_URL = f"{CONVERSATION_URL}/messages"
MESSAGE_URL = f"{MESSAGES_URL}/{MESSAGE_ID}"

SAMPLE_CONVERSATION = ConversationResponse(
    conversation_id=CONVERSATION_ID,
    title="Test Chat",
    model="gpt-4o",
    status="active",
    created_at=FIXED_TS,
)

SAMPLE_CONVERSATION_JSON = {
    "conversationId": CONVERSATION_ID,
    "title": "Test Chat",
    "model": "gpt-4o",
    "status": "active",
    "createdAt": FIXED_TS.isoformat(),
}

SAMPLE_MESSAGE = MessageResponse(
    message_id=MESSAGE_ID,
    conversation_id=CONVERSATION_ID,
    content="Hello",
    role="user",
    timestamp=FIXED_TS,
)

SAMPLE_MESSAGE_JSON = {
    "messageId": MESSAGE_ID,
    "conversationId": CONVERSATION_ID,
    "content": "Hello",
    "role": "user",
    "timestamp": FIXED_TS.isoformat(),
}


class TestListConversations:
    def test_returns_conversations(self, client):
        with patch("app.api.chat.routes.list_conversations_service", return_value=[SAMPLE_CONVERSATION]):
            response = client.get(CONVERSATIONS_URL)

        assert response.status_code == 200
        assert response.get_json() == {"items": [SAMPLE_CONVERSATION_JSON]}

    def test_empty_result(self, client):
        with patch("app.api.chat.routes.list_conversations_service", return_value=[]):
            response = client.get(CONVERSATIONS_URL)

        assert response.status_code == 200
        assert response.get_json() == {"items": []}

    def test_response_is_camel_case(self, client):
        with patch("app.api.chat.routes.list_conversations_service", return_value=[SAMPLE_CONVERSATION]):
            data = client.get(CONVERSATIONS_URL).get_json()

        item = data["items"][0]
        assert "conversationId" in item
        assert "createdAt" in item
        assert "conversation_id" not in item
        assert "created_at" not in item


class TestCreateConversation:
    def test_creates_conversation(self, client):
        with patch("app.api.chat.routes.create_conversation_service", return_value=SAMPLE_CONVERSATION) as mock:
            response = client.post(CONVERSATIONS_URL, json={"title": "Test Chat", "model": "gpt-4o"})
            called_req = mock.call_args[0][0]
            assert called_req.title == "Test Chat"
            assert called_req.model == "gpt-4o"

        assert response.status_code == 201
        assert response.get_json() == {"conversation": SAMPLE_CONVERSATION_JSON}

    def test_uses_defaults_when_body_empty(self, client):
        with patch("app.api.chat.routes.create_conversation_service", return_value=SAMPLE_CONVERSATION) as mock:
            client.post(CONVERSATIONS_URL, json={})
            called_req = mock.call_args[0][0]
            assert called_req.title == "New Conversation"
            assert called_req.model == "gpt-4o"

    def test_no_body_uses_defaults(self, client):
        with patch("app.api.chat.routes.create_conversation_service", return_value=SAMPLE_CONVERSATION):
            response = client.post(CONVERSATIONS_URL)

        assert response.status_code == 201


class TestGetConversation:
    def test_returns_conversation(self, client):
        with patch("app.api.chat.routes.get_conversation_service", return_value=SAMPLE_CONVERSATION):
            response = client.get(CONVERSATION_URL)

        assert response.status_code == 200
        assert response.get_json() == {"conversation": SAMPLE_CONVERSATION_JSON}

    def test_not_found_returns_404(self, client):
        from app.common.error_handler import NotFoundError
        with patch("app.api.chat.routes.get_conversation_service", side_effect=NotFoundError()):
            response = client.get(CONVERSATION_URL)

        assert response.status_code == 404


class TestUpdateConversation:
    def test_updates_conversation(self, client):
        updated = ConversationResponse(
            conversation_id=CONVERSATION_ID,
            title="Renamed",
            model="gpt-4o",
            status="active",
            created_at=FIXED_TS,
        )
        with patch("app.api.chat.routes.update_conversation_service", return_value=updated) as mock:
            response = client.put(CONVERSATION_URL, json={"title": "Renamed"})
            assert mock.call_args[0][0] == CONVERSATION_ID
            assert mock.call_args[0][1].title == "Renamed"

        assert response.status_code == 200
        assert response.get_json()["conversation"]["title"] == "Renamed"

    def test_not_found_returns_404(self, client):
        from app.common.error_handler import NotFoundError
        with patch("app.api.chat.routes.update_conversation_service", side_effect=NotFoundError()):
            response = client.put(CONVERSATION_URL, json={"title": "X"})

        assert response.status_code == 404


class TestDeleteConversation:
    def test_deletes_conversation(self, client):
        with patch("app.api.chat.routes.delete_conversation_service"):
            response = client.delete(CONVERSATION_URL)

        assert response.status_code == 204

    def test_not_found_returns_404(self, client):
        from app.common.error_handler import NotFoundError
        with patch("app.api.chat.routes.delete_conversation_service", side_effect=NotFoundError()):
            response = client.delete(CONVERSATION_URL)

        assert response.status_code == 404


class TestGetMessages:
    def test_returns_messages(self, client):
        with patch("app.api.chat.routes.get_recent_messages", return_value=[SAMPLE_MESSAGE]) as mock:
            response = client.get(MESSAGES_URL)
            mock.assert_called_once_with(CONVERSATION_ID, limit=50)

        assert response.status_code == 200
        assert response.get_json() == {"items": [SAMPLE_MESSAGE_JSON]}

    def test_passes_limit_param(self, client):
        with patch("app.api.chat.routes.get_recent_messages", return_value=[]) as mock:
            client.get(f"{MESSAGES_URL}?limit=10")
            mock.assert_called_once_with(CONVERSATION_ID, limit=10)

    def test_response_is_camel_case(self, client):
        with patch("app.api.chat.routes.get_recent_messages", return_value=[SAMPLE_MESSAGE]):
            data = client.get(MESSAGES_URL).get_json()

        item = data["items"][0]
        assert "messageId" in item
        assert "conversationId" in item
        assert "message_id" not in item
        assert "conversation_id" not in item

    def test_empty_result(self, client):
        with patch("app.api.chat.routes.get_recent_messages", return_value=[]):
            response = client.get(MESSAGES_URL)

        assert response.status_code == 200
        assert response.get_json() == {"items": []}


class TestCreateMessage:
    def test_creates_message(self, client):
        with patch("app.api.chat.routes.create_message_service", return_value=SAMPLE_MESSAGE) as mock:
            response = client.post(MESSAGES_URL, json={"content": "Hello", "role": "user"})
            assert mock.call_args[0][0] == CONVERSATION_ID
            called_req = mock.call_args[0][1]
            assert called_req.content == "Hello"
            assert called_req.role == "user"

        assert response.status_code == 201
        assert response.get_json() == {"message": SAMPLE_MESSAGE_JSON}

    def test_response_is_camel_case(self, client):
        with patch("app.api.chat.routes.create_message_service", return_value=SAMPLE_MESSAGE):
            data = client.post(MESSAGES_URL, json={"content": "Hello", "role": "user"}).get_json()

        msg = data["message"]
        assert "messageId" in msg
        assert "conversationId" in msg
        assert "message_id" not in msg
        assert "conversation_id" not in msg

    def test_missing_content_returns_400(self, client):
        response = client.post(MESSAGES_URL, json={"role": "user"})
        assert response.status_code == 400

    def test_missing_role_returns_400(self, client):
        response = client.post(MESSAGES_URL, json={"content": "Hello"})
        assert response.status_code == 400

    def test_no_body_returns_400(self, client):
        response = client.post(MESSAGES_URL)
        assert response.status_code == 400


class TestGetMessage:
    def test_returns_message(self, client):
        with patch("app.api.chat.routes.get_message_service", return_value=SAMPLE_MESSAGE):
            response = client.get(MESSAGE_URL)

        assert response.status_code == 200
        assert response.get_json() == {"message": SAMPLE_MESSAGE_JSON}

    def test_not_found_returns_404(self, client):
        from app.common.error_handler import NotFoundError
        with patch("app.api.chat.routes.get_message_service", side_effect=NotFoundError()):
            response = client.get(MESSAGE_URL)

        assert response.status_code == 404


class TestDeleteMessage:
    def test_deletes_message(self, client):
        with patch("app.api.chat.routes.delete_message_service"):
            response = client.delete(MESSAGE_URL)

        assert response.status_code == 204

    def test_not_found_returns_404(self, client):
        from app.common.error_handler import NotFoundError
        with patch("app.api.chat.routes.delete_message_service", side_effect=NotFoundError()):
            response = client.delete(MESSAGE_URL)

        assert response.status_code == 404
