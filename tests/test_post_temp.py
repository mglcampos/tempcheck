

import json
import unittest

from tempcheck.api.app import app


class TestPostTemp(unittest.TestCase):
    """Test the post temperature data endpoint."""

    def __init__(self, *args, **kwargs):
        """Initializes the test case and loads the necessary data."""
        super(TestPostTemp, self).__init__(*args, **kwargs)
        self.data = {'siteId': 'abc123', 'orgId': 'alphacorp', 'temperature': '27.3', 'timestamp': '1658739178'}

    def test_post_temperature(self):
        """Test the post temperature endpoint with a good request."""
        with app.test_client() as client:
            res = client.post('/temperature', json=self.data)
            self.assertTrue(res.status_code == 200)
            res_d = json.loads(res.data)
            self.assertTrue(res_d['status'] == 'Success!',
                            'Output dictionary does not contain custom success status.')

    def test_post_temperature_errors(self):
        """Test the post temperature endpoint with badly formatted requests."""
        with app.test_client() as client:
            ## test missing data case
            res1 = client.post('/temperature', json={})
            self.assertTrue(res1.status_code == 400, 'Empty json data does not cause error 400.')
            self.assertTrue(json.loads(res1.data)['message'][0] == 'Missing JSON data', 'Wrong error message.')

            ## test wrong attribute name case
            data = self.data.copy()
            k = list(data.keys())[0]
            data[k+'_'] = data.pop(k)
            res2 = client.post('/temperature', json=data)
            self.assertTrue(res2.status_code == 400, 'Wrong attribute name does not cause error 400.')
            self.assertTrue(json.loads(res2.data)['message'][0] == f'Attribute {k} is missing', 'Wrong error message')

            ## test wrong media type
            res3 = client.post('/temperature')
            self.assertTrue(res3.status_code == 415, 'Wrong media type does not cause error 415.')

