import pytest

CONVERSATIONS_URL = "/chat/conversations"
MISSING_ID = "00000000-0000-0000-0000-000000000000"


# ---------------------------------------------------------------------------
# Seed fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def conversation(client):
    response = client.post(CONVERSATIONS_URL, json={"title": "Test Chat", "model": "gpt-4o"})
    assert response.status_code == 201
    return response.get_json()["conversation"]


@pytest.fixture
def message(client, conversation):
    url = f"{CONVERSATIONS_URL}/{conversation['conversationId']}/messages"
    response = client.post(url, json={"content": "Hello", "role": "user"})
    assert response.status_code == 201
    return response.get_json()["message"]


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

class TestListConversations:
    def test_returns_seeded_conversations(self, client):
        client.post(CONVERSATIONS_URL, json={"title": "First"})
        client.post(CONVERSATIONS_URL, json={"title": "Second"})

        response = client.get(CONVERSATIONS_URL)

        assert response.status_code == 200
        items = response.get_json()["items"]
        assert len(items) == 2
        titles = {c["title"] for c in items}
        assert titles == {"First", "Second"}

    def test_empty_when_no_conversations(self, client):
        response = client.get(CONVERSATIONS_URL)

        assert response.status_code == 200
        assert response.get_json() == {"items": []}

    def test_response_is_camel_case(self, client, conversation):
        data = client.get(CONVERSATIONS_URL).get_json()

        item = data["items"][0]
        assert "conversationId" in item
        assert "createdAt" in item
        assert "conversation_id" not in item
        assert "created_at" not in item


class TestCreateConversation:
    def test_creates_with_provided_fields(self, client):
        response = client.post(CONVERSATIONS_URL, json={"title": "My Chat", "model": "gpt-4o-mini"})

        assert response.status_code == 201
        conv = response.get_json()["conversation"]
        assert conv["title"] == "My Chat"
        assert conv["model"] == "gpt-4o-mini"
        assert conv["status"] == "active"
        assert "conversationId" in conv
        assert "createdAt" in conv

    def test_persists_to_db(self, client):
        post_resp = client.post(CONVERSATIONS_URL, json={"title": "Persisted"})
        conv_id = post_resp.get_json()["conversation"]["conversationId"]

        get_resp = client.get(f"{CONVERSATIONS_URL}/{conv_id}")
        assert get_resp.status_code == 200
        assert get_resp.get_json()["conversation"]["title"] == "Persisted"

    def test_uses_defaults_for_empty_body(self, client):
        response = client.post(CONVERSATIONS_URL, json={})

        assert response.status_code == 201
        conv = response.get_json()["conversation"]
        assert conv["title"] == "New Conversation"
        assert conv["model"] == "gpt-4o"

    def test_no_body_uses_defaults(self, client):
        response = client.post(CONVERSATIONS_URL)

        assert response.status_code == 201


class TestGetConversation:
    def test_returns_conversation(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.get(f"{CONVERSATIONS_URL}/{conv_id}")

        assert response.status_code == 200
        assert response.get_json()["conversation"]["conversationId"] == conv_id

    def test_not_found_returns_404(self, client):
        response = client.get(f"{CONVERSATIONS_URL}/{MISSING_ID}")

        assert response.status_code == 404


class TestUpdateConversation:
    def test_updates_title(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.put(f"{CONVERSATIONS_URL}/{conv_id}", json={"title": "Renamed"})

        assert response.status_code == 200
        assert response.get_json()["conversation"]["title"] == "Renamed"

    def test_updates_status(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.put(f"{CONVERSATIONS_URL}/{conv_id}", json={"status": "archived"})

        assert response.status_code == 200
        assert response.get_json()["conversation"]["status"] == "archived"

    def test_persists_update_to_db(self, client, conversation):
        conv_id = conversation["conversationId"]
        client.put(f"{CONVERSATIONS_URL}/{conv_id}", json={"title": "Updated"})

        get_resp = client.get(f"{CONVERSATIONS_URL}/{conv_id}")
        assert get_resp.get_json()["conversation"]["title"] == "Updated"

    def test_not_found_returns_404(self, client):
        response = client.put(f"{CONVERSATIONS_URL}/{MISSING_ID}", json={"title": "X"})

        assert response.status_code == 404


class TestDeleteConversation:
    def test_deletes_conversation(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.delete(f"{CONVERSATIONS_URL}/{conv_id}")

        assert response.status_code == 204

    def test_deleted_conversation_is_gone(self, client, conversation):
        conv_id = conversation["conversationId"]
        client.delete(f"{CONVERSATIONS_URL}/{conv_id}")

        get_resp = client.get(f"{CONVERSATIONS_URL}/{conv_id}")
        assert get_resp.status_code == 404

    def test_not_found_returns_404(self, client):
        response = client.delete(f"{CONVERSATIONS_URL}/{MISSING_ID}")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

class TestGetMessages:
    def test_returns_seeded_messages(self, client, conversation):
        conv_id = conversation["conversationId"]
        messages_url = f"{CONVERSATIONS_URL}/{conv_id}/messages"
        client.post(messages_url, json={"content": "First", "role": "user"})
        client.post(messages_url, json={"content": "Second", "role": "assistant"})

        response = client.get(messages_url)

        assert response.status_code == 200
        assert len(response.get_json()["items"]) == 2

    def test_empty_when_no_messages(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.get(f"{CONVERSATIONS_URL}/{conv_id}/messages")

        assert response.status_code == 200
        assert response.get_json() == {"items": []}

    def test_limit_param_restricts_results(self, client, conversation):
        conv_id = conversation["conversationId"]
        messages_url = f"{CONVERSATIONS_URL}/{conv_id}/messages"
        for i in range(5):
            client.post(messages_url, json={"content": f"msg {i}", "role": "user"})

        response = client.get(f"{messages_url}?limit=2")

        assert response.status_code == 200
        assert len(response.get_json()["items"]) == 2

    def test_response_is_camel_case(self, client, message, conversation):
        conv_id = conversation["conversationId"]
        data = client.get(f"{CONVERSATIONS_URL}/{conv_id}/messages").get_json()

        item = data["items"][0]
        assert "messageId" in item
        assert "conversationId" in item
        assert "message_id" not in item
        assert "conversation_id" not in item


class TestCreateMessage:
    def test_creates_message(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.post(
            f"{CONVERSATIONS_URL}/{conv_id}/messages",
            json={"content": "Hello", "role": "user"},
        )

        assert response.status_code == 201
        msg = response.get_json()["message"]
        assert msg["content"] == "Hello"
        assert msg["role"] == "user"
        assert msg["conversationId"] == conv_id
        assert "messageId" in msg
        assert "timestamp" in msg

    def test_persists_to_db(self, client, conversation):
        conv_id = conversation["conversationId"]
        post_resp = client.post(
            f"{CONVERSATIONS_URL}/{conv_id}/messages",
            json={"content": "Persisted", "role": "user"},
        )
        msg_id = post_resp.get_json()["message"]["messageId"]

        get_resp = client.get(f"{CONVERSATIONS_URL}/{conv_id}/messages/{msg_id}")
        assert get_resp.status_code == 200
        assert get_resp.get_json()["message"]["content"] == "Persisted"

    def test_response_is_camel_case(self, client, conversation):
        conv_id = conversation["conversationId"]
        data = client.post(
            f"{CONVERSATIONS_URL}/{conv_id}/messages",
            json={"content": "Hello", "role": "user"},
        ).get_json()

        msg = data["message"]
        assert "messageId" in msg
        assert "conversationId" in msg
        assert "message_id" not in msg
        assert "conversation_id" not in msg

    def test_missing_content_returns_400(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.post(
            f"{CONVERSATIONS_URL}/{conv_id}/messages", json={"role": "user"}
        )
        assert response.status_code == 400

    def test_missing_role_returns_400(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.post(
            f"{CONVERSATIONS_URL}/{conv_id}/messages", json={"content": "Hello"}
        )
        assert response.status_code == 400

    def test_no_body_returns_400(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.post(f"{CONVERSATIONS_URL}/{conv_id}/messages")
        assert response.status_code == 400


class TestGetMessage:
    def test_returns_message(self, client, message, conversation):
        conv_id = conversation["conversationId"]
        msg_id = message["messageId"]
        response = client.get(f"{CONVERSATIONS_URL}/{conv_id}/messages/{msg_id}")

        assert response.status_code == 200
        assert response.get_json()["message"]["messageId"] == msg_id

    def test_not_found_returns_404(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.get(f"{CONVERSATIONS_URL}/{conv_id}/messages/{MISSING_ID}")

        assert response.status_code == 404


class TestDeleteMessage:
    def test_deletes_message(self, client, message, conversation):
        conv_id = conversation["conversationId"]
        msg_id = message["messageId"]
        response = client.delete(f"{CONVERSATIONS_URL}/{conv_id}/messages/{msg_id}")

        assert response.status_code == 204

    def test_deleted_message_is_gone(self, client, message, conversation):
        conv_id = conversation["conversationId"]
        msg_id = message["messageId"]
        client.delete(f"{CONVERSATIONS_URL}/{conv_id}/messages/{msg_id}")

        get_resp = client.get(f"{CONVERSATIONS_URL}/{conv_id}/messages/{msg_id}")
        assert get_resp.status_code == 404

    def test_not_found_returns_404(self, client, conversation):
        conv_id = conversation["conversationId"]
        response = client.delete(f"{CONVERSATIONS_URL}/{conv_id}/messages/{MISSING_ID}")

        assert response.status_code == 404
