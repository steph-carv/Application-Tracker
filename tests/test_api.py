from tests.conftest import auth_headers
PASSWORD = "testpass123"


def test_create_and_list_season(client):
    headers = auth_headers(client, "user1@example.com")
    response = client.post("/seasons", json={"name": "Placement 2027"}, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Placement 2027"

    response = client.get("/seasons", headers=headers)
    assert len(response.json()) == 1

def test_signup_dupe(client):
    response = client.post("/auth/signup", json={"email":"FAKE@example.com", "password": "fakehashedpassword" })
    assert response.status_code == 201
    response = client.post("/auth/signup", json={"email":"fake@example.com", "password": "fakehashedpassword" })
    assert response.status_code == 409

def test_login_wrong_password(client):
    response = client.post("/auth/signup", json={"email":"fake@example.com", "password": "passwordone" })
    assert response.status_code == 201
    response = client.post("/auth/login", data={"username":"fake@example.com", "password": "wrongpassword" })
    assert response.status_code == 401

def test_wrong_email(client):
    response = client.post("/auth/signup", json={"email":"fake@example.com", "password": "passwordone" })
    assert response.status_code == 201
    response = client.post("/auth/login", data={"username":"wrongfake@example.com", "password": "passwordone" })
    assert response.status_code == 401    


def test_get_seasons(client):
    response = client.get("/seasons")
    assert response.status_code == 401

def test_user2_cannot_access_user1_seasons(client):
    headers1 = auth_headers(client, "user1@example.com")
    response = client.post("/seasons", json={"name": "Test Year 20XX"}, headers = headers1)
    assert response.status_code == 201
    season_id = response.json()["id"]
    headers2 = auth_headers(client, "user2@example.com")
    response = client.get(f"/seasons/{season_id}", headers=headers2)
    assert response.status_code == 404
    response = client.get("/seasons", headers=headers2)
    assert response.status_code == 200
    assert response.json() == []   



def test_patch_cannot_change_stage(client):
    headers = auth_headers(client, "user1@example.com", PASSWORD)
    response = client.post("/seasons", json={"name": "Placement 2027"}, headers=headers)
    assert response.status_code == 201
    season_id = response.json()["id"]

    response = client.post(
        "/applications",
        json={"season_id": season_id, "company": "Deloitte", "position": "Tech Placement"},
        headers=headers,
    )
    assert response.status_code == 201
    application_id = response.json()["id"]
    assert response.json()["current_stage"] == "To Apply"

    response = client.patch(
        f"/applications/{application_id}",
        json={"current_stage": "Offer", "notes": "testing"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["notes"] == "testing"
    assert response.json()["current_stage"] == "To Apply"


def test_delete_season_requires_password_and_cascades(client):
    headers = auth_headers(client, "user1@example.com", PASSWORD)
    response = client.post("/seasons", json={"name": "Placement 2027"}, headers=headers)
    assert response.status_code == 201
    season_id = response.json()["id"]

    response = client.post(
        "/applications",
        json={"season_id": season_id, "company": "Deloitte", "position": "Tech Placement"},
        headers=headers,
    )
    assert response.status_code == 201
    application_id = response.json()["id"]

    response = client.post(f"/seasons/{season_id}/delete", json={"password": "wrongpassword"}, headers=headers)
    assert response.status_code == 403
    response = client.get(f"/seasons/{season_id}", headers=headers)
    assert response.status_code == 200

    response = client.post(f"/seasons/{season_id}/delete", json={"password": PASSWORD}, headers=headers)
    assert response.status_code == 204
    response = client.get(f"/seasons/{season_id}", headers=headers)
    assert response.status_code == 404
    response = client.get(f"/applications/{application_id}", headers=headers)
    assert response.status_code == 404
