import json
from unittest.mock import patch, MagicMock
from pymongo.errors import ServerSelectionTimeoutError
from app import app


def test_default_mongo_uri_is_configured():
    assert 'cluster0.oysibhp.mongodb.net' in app.MONGO_URI


def test_placeholder_password_raises_clear_error():
    with patch('app.MONGO_URI', 'mongodb+srv://<username>:<password>@cluster0.mongodb.net/test?retryWrites=true&w=majority'):
        try:
            app.get_db_collection()
        except ValueError as exc:
            assert 'Replace <db_password>' in str(exc)
        else:
            raise AssertionError('Expected a ValueError for placeholder MongoDB password')


def run_tests():
    client = app.test_client()

    print("--- Test 1: GET /api endpoint ---")
    res = client.get('/api')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    print("PASS: /api returned JSON list successfully.")

    print("\n--- Test 2: GET / form page ---")
    res = client.get('/')
    assert res.status_code == 200
    assert b"Submit Data" in res.data
    print("PASS: Form page rendered correctly.")

    print("\n--- Test 3: POST /submit missing fields (Error on same page, no redirect) ---")
    res = client.post('/submit', data={'name': 'Jane Doe', 'email': '', 'message': ''})
    assert res.status_code == 400
    assert b"Please fill in all required fields" in res.data
    assert b"Submission Error" in res.data
    print("PASS: Missing fields error displayed on form page without redirect.")

    print("\n--- Test 4: POST /submit uses the default MongoDB URI and surfaces connection errors ---")
    with patch('app.get_db_collection', side_effect=ServerSelectionTimeoutError('timeout')):
        res = client.post('/submit', data={'name': 'Jane Doe', 'email': 'jane@example.com', 'message': 'Hello world'})
    assert res.status_code == 500
    assert b"Could not connect to MongoDB Atlas" in res.data
    assert b"Submission Error" in res.data
    print("PASS: Default MongoDB URI is used and connection errors are rendered on the form page.")

    print("\n--- Test 5: POST /submit with Successful MongoDB Insert (Redirect to /success) ---")
    mock_collection = MagicMock()
    mock_collection.insert_one.return_value = MagicMock(inserted_id="12345")
    with patch('app.get_db_collection', return_value=mock_collection):
        res = client.post('/submit', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'General',
            'message': 'Testing successful insertion'
        })
        assert res.status_code == 302
        assert '/success' in res.headers['Location']
        print("PASS: Successful insert redirected to /success.")

    print("\n--- Test 6: GET /success confirmation page ---")
    res = client.get('/success')
    assert res.status_code == 200
    assert b"Data submitted successfully" in res.data
    print("PASS: Success page displays 'Data submitted successfully'.")

    print("\nALL 6 TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
