
from datetime import datetime

class TempEvaluator:
    """Class responsible for evaluating the temperature data collected from sensors."""
    def __init__(self, db: object):
        """Initializes the temp evaluator object.

        Args:
            db (object): Database connection object.
        """
        if db is None:
            raise Exception('Database connection unavailable.')
        self.db = db

    def eval_temp(self, siteId: str, orgId: str, threshold: float = 30) -> str:
        """Evaluates the temperature given a threshold. Only looks at the last temperature reading for the current day.

         Args:
            siteId (str): Site id.
            orgId (str): Organization id.
            siteId (str): Site id.
            threshold (int): Temp eval threshold

         Returns:
            str: Temperature evaluation.
        """
        c = self.db.cursor()
        row = c.execute(f"""SELECT * FROM test Where siteId = '{siteId}' and orgId = '{orgId}' ORDER BY timestamp DESC LIMIT 1;""").fetchone()

        time = datetime.fromtimestamp(row[3])
        curr_time = datetime.now()
        if time.day != curr_time.day:
            raise Exception('Not temperature data for today.')

        temp = row[2]

        if float(temp) > threshold:
            return "Too hot"
        else:
            return "Not too hot"
