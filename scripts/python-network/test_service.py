from unittest.mock import patch

from service import get_user

@patch("service.get")
def test_get_user(mock_get):
    mock_get.return_value.json.return_value = {
        "id": 1,
        "name": "Mike"
    }

    result = get_user(1)

    assert result["name"] == "Mike"
