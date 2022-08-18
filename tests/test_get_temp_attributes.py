
from tempcheck.api.temp_attributes import temp_attributes
from tempcheck.api.app import app


def test_get_temp_attributes():
    """Test the get temp attributes endpoint."""
    with app.test_client() as client:
        response = client.get("/temp_attributes")
        assert response.json == temp_attributes
