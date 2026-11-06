def test_requires_auth(client):
    assert client.put("/api/settings/profile", json={"full_name": "X"}).status_code == 401


def test_update_profile(client, auth_headers):
    res = client.put("/api/settings/profile", json={"full_name": "New Name"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["full_name"] == "New Name"
    assert client.get("/api/users/me", headers=auth_headers).json()["full_name"] == "New Name"


def test_update_profile_rejects_blank_name(client, auth_headers):
    assert client.put("/api/settings/profile", json={"full_name": ""}, headers=auth_headers).status_code == 422


def test_change_password_success_and_relogin(client, auth_headers, user_payload):
    res = client.put(
        "/api/settings/password",
        json={"current_password": user_payload["password"], "new_password": "newpassword123"},
        headers=auth_headers,
    )
    assert res.status_code == 204
    old = client.post("/api/auth/login", data={"username": user_payload["email"], "password": user_payload["password"]})
    assert old.status_code == 401
    new = client.post("/api/auth/login", data={"username": user_payload["email"], "password": "newpassword123"})
    assert new.status_code == 200


def test_change_password_wrong_current(client, auth_headers):
    res = client.put(
        "/api/settings/password", json={"current_password": "wrong", "new_password": "newpassword123"}, headers=auth_headers
    )
    assert res.status_code == 401


def test_delete_account_wrong_password(client, auth_headers):
    assert client.post("/api/settings/delete-account", json={"password": "wrong"}, headers=auth_headers).status_code == 401


def test_delete_account_success(client, auth_headers, user_payload):
    res = client.post("/api/settings/delete-account", json={"password": user_payload["password"]}, headers=auth_headers)
    assert res.status_code == 204
    assert client.get("/api/users/me", headers=auth_headers).status_code == 401
    relogin = client.post("/api/auth/login", data={"username": user_payload["email"], "password": user_payload["password"]})
    assert relogin.status_code == 401
