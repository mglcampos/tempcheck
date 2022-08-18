
import json
import sqlite3
import unittest
from datetime import datetime

from tempcheck.api.app import app


class TestGetTempEvaluation(unittest.TestCase):
    """Test the get temperature evaluation endpoint."""

    def __init__(self, *args, **kwargs):
        """Initializes the test case and loads the necessary data."""
        super(TestGetTempEvaluation, self).__init__(*args, **kwargs)
        self.DATABASE = 'test.db'
        self.siteId = 'abc123'
        self.orgId = 'alphacorp'

    def setUp(self):
        """Set up the test environment"""
        self.db = sqlite3.connect(self.DATABASE)
        c = self.db.cursor()
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Test' ''')
        if c.fetchone()[0] == 1:
            c = self.db.cursor()
            c.execute("DROP TABLE Test")
        c.execute(
                """CREATE TABLE Test (siteId VARCHAR(255), orgId VARCHAR(255), temperature DECIMAL(10, 5), timestamp INTEGER);""")
        c.execute(("""CREATE UNIQUE INDEX idx_timestamp ON test (timestamp);"""))
        t1 = int(datetime.now().timestamp()) -2
        insert_query = f"""INSERT INTO Test (siteId, orgId, temperature, timestamp) VALUES ('{self.siteId}','{self.orgId}','74.1','{t1}')"""
        count = c.execute(insert_query)
        t2 = int(datetime.now().timestamp())
        insert_query = f"""INSERT INTO Test (siteId, orgId, temperature, timestamp) VALUES ('{self.siteId}','{self.orgId}','74.5','{t2}')"""
        count = c.execute(insert_query)
        self.db.commit()

    def tearDown(self):
        """Tear down the test environment"""
        c = self.db.cursor()
        c.execute("DROP TABLE Test")
        self.db.commit()
        self.db.close()

    def test_get_temp_eval(self):
        """Test the get temperature evaluation endpoint with a good request."""
        with app.test_client() as client:
            res = client.get('/toohotornot', query_string={'siteId': self.siteId})
            self.assertTrue(res.status_code == 200)
            res_d = json.loads(res.data)
            self.assertTrue('eval' in res_d.keys(),
                            'Output dictionary does not contain evaluation')
            ## Assuming the output is a probability
            self.assertTrue(res_d['eval'] in ['Too hot', 'Not too hot'], 'Prediction value is out of range [0,1].')

    def test_get_temp_eval_errors(self):
        """Test the get temp eval endpoint with badly formatted requests."""
        with app.test_client() as client:
            ## test missing data case
            res = client.get('/toohotornot')
            self.assertTrue(res.status_code == 400, 'Missing argument does not cause error 400.')
