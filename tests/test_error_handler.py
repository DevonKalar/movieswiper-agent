class TestRouteNotFound:
    def test_unknown_route_returns_404(self, client):
        response = client.get("/does/not/exist")

        assert response.status_code == 404
        assert response.get_json() == {"message": "Not found", "error_code": "NOT_FOUND"}

    def test_unknown_nested_route_returns_404(self, client):
        response = client.post("/chat/conversations/fake-id/fake-resource")

        assert response.status_code == 404

    def test_wrong_method_is_not_404(self, client):
        # Flask returns 405 for wrong method on a known route, not 404
        response = client.patch("/chat/conversations")

        assert response.status_code != 404
