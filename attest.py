
import uuid

import pytest
import requests

BASE_URL = "http://localhost:8080"
TIMEOUT = 180


def make_payload(prefix):
    unique_id = uuid.uuid4().hex[:8]

    return {
        "page": f"{prefix}-{unique_id}-Page",
        "title": f"{prefix}-{unique_id}-Title",
        "context": (
            f"{prefix} Context. Allied Testing provides "
            "software quality assurance and testing services."
        )
    }


def api_request(method, path, **kwargs):
    return requests.request(
        method,
        f"{BASE_URL}{path}",
        timeout=TIMEOUT,
        **kwargs
    )


def create_page(payload):
    response = api_request(
        "POST",
        "/at_data/",
        json=payload
    )

    assert response.status_code == 201, response.text
    return response.json()["id"]


def cleanup_page(page_id):
    response = api_request(
        "DELETE",
        f"/at_data/{page_id}"
    )

    assert response.status_code in (200, 404), response.text


def test_add_page():
    payload = make_payload("Add")
    page_id = None

    try:
        page_id = create_page(payload)

        response = api_request(
            "GET",
            f"/at_data/{page_id}"
        )

        assert response.status_code == 200, response.text

        data = response.json()

        assert data["page"] == payload["page"]
        assert data["title"] == payload["title"]
        assert data["context"] == payload["context"]

        assert data["page_vector"] is not None
        assert data["title_vector"] is not None
        assert data["context_vector"] is not None

    finally:
        if page_id is not None:
            cleanup_page(page_id)


def test_show_pages():
    response = api_request("GET", "/at_data/")

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_invalid_page():
    response = api_request(
        "POST",
        "/at_data/",
        json={
            "page": "",
            "title": "",
            "context": ""
        }
    )

    assert response.status_code == 400, response.text


def test_update_page():
    payload = make_payload("Update")
    page_id = None

    try:
        page_id = create_page(payload)

        updated_payload = {
            "page": payload["page"],
            "title": "Updated Test Title",
            "context": (
                "Updated test context describing software "
                "quality assurance services."
            )
        }

        response = api_request(
            "PUT",
            f"/at_data/{page_id}",
            json=updated_payload
        )

        assert response.status_code == 200, response.text
        assert response.json()["message"] == "Updated"

        response = api_request(
            "GET",
            f"/at_data/{page_id}"
        )

        assert response.status_code == 200, response.text

        data = response.json()

        assert data["title"] == updated_payload["title"]
        assert data["context"] == updated_payload["context"]
        assert data["context_vector"] is not None

    finally:
        if page_id is not None:
            cleanup_page(page_id)


def test_delete_page():
    payload = make_payload("Delete")
    page_id = create_page(payload)

    try:
        response = api_request(
            "DELETE",
            f"/at_data/{page_id}"
        )

        assert response.status_code == 200, response.text
        assert response.json()["message"] == "Deleted"

        response = api_request(
            "GET",
            f"/at_data/{page_id}"
        )

        assert response.status_code == 404, response.text

    finally:
        cleanup_page(page_id)


def test_get_page_by_id():
    payload = make_payload("GetById")
    page_id = None

    try:
        page_id = create_page(payload)

        response = api_request(
            "GET",
            f"/at_data/{page_id}"
        )

        assert response.status_code == 200, response.text
        assert response.json()["id"] == page_id
        assert response.json()["title"] == payload["title"]

    finally:
        if page_id is not None:
            cleanup_page(page_id)


def test_get_nonexistent_page():
    response = api_request(
        "GET",
        "/at_data/2147483647"
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Record not found"


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-v", __file__]))
