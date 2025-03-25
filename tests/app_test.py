import json
from pathlib import Path

import pytest

from project.app import app, db, models

TEST_DB = "test.db"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["TestUser"] = "Bob"
    app.config["TestPassword"] = "abc123"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///:memory:"

    with app.app_context():
        db.create_all()  # setup
        # create a test user
        testuser = models.User(app.config["TestUser"], app.config["TestPassword"])
        db.session.add(testuser)
        db.session.commit()
        yield app.test_client()  # tests run here
        db.drop_all()  # teardown


def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Logout helper function"""
    return client.get("/logout", follow_redirects=True)

def create_user(client, username, password):
    """User creation helper function"""
    return client.post(
        "/newuser",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def test_index(client):
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200

def test_empty_db(client):
    """Ensure database is blank"""
    rv = client.get("/")
    assert b"No entries yet. Add some!" in rv.data

def test_user_creation(client):
    """Ensure the user doesn't exist at the start, then does exist at the end"""
    response = login(client, "jeff", "mypass")
    assert b"Invalid username or password" in response.data
    response = create_user(client, "jeff", "mypass")
    assert b"New User Created" in response.data
    response = login(client, "jeff", "mypass")
    assert b"You were logged in" in response.data

def test_login_logout(client):
    """Test login and logout using helper functions"""
    rv = login(client, app.config["TestUser"], app.config["TestPassword"])
    assert b"You were logged in" in rv.data
    rv = logout(client)
    assert b"You were logged out" in rv.data
    rv = login(client, app.config["TestUser"] + "x", app.config["TestPassword"])
    assert b"Invalid username or password" in rv.data
    rv = login(client, app.config["TestUser"], app.config["TestPassword"] + "x")
    assert b"Invalid username or password" in rv.data


def test_messages(client):
    """Ensure that user can post messages"""
    login(client, app.config["TestUser"], app.config["TestPassword"])
    rv = client.post(
        "/add",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"No entries here so far" not in rv.data
    assert b"&lt;Hello&gt;" in rv.data
    assert b"<strong>HTML</strong> allowed here" in rv.data


def test_delete_message(client):
    """Ensure the messages are being deleted"""
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 0
    login(client, app.config["TestUser"], app.config["TestPassword"])
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 1
