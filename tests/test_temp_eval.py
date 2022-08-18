
import unittest
import sqlite3
from datetime import datetime

from tempcheck.evaluators.temp_eval import TempEvaluator

class TestTempEvaluator(unittest.TestCase):
    """Test the TempEvaluator class."""

    def __init__(self, *args, **kwargs):
        """Initializes the test case and loads the necessary data."""
        super(TestTempEvaluator, self).__init__(*args, **kwargs)
        self.DATABASE = 'test.db'

    def setUp(self):
        """Set up the test environment"""
        self.siteId = 'abc123'
        self.orgId = 'alphacorp'
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
        self.evaluator = TempEvaluator(db=self.db)

    def tearDown(self):
        """Tear down the test environment"""
        c = self.db.cursor()
        c.execute("DROP TABLE Test")
        self.db.commit()
        self.db.close()

    def test_temp_eval(self):
        """Tests the evaluation method."""
        eval = self.evaluator.eval_temp(siteId=self.siteId, orgId=self.orgId)
        assert eval == 'Too hot', 'Bad evaluation'
        eval = self.evaluator.eval_temp(siteId=self.siteId, orgId=self.orgId, threshold=100)
        assert eval == 'Not too hot', 'Bad evaluation'
