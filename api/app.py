
import json
import sqlite3
from flask import Flask
from flask import g
from flask import request
from flask import Response

from tempcheck.api.temp_attributes import temp_attributes
from tempcheck.evaluators.temp_eval import TempEvaluator

############################
## Improvements
# - Missing versioning, to enable scaling the api versioning is essential. Can be done by using the header or the URI.
# - Add security, use authentication to secure the API.
# - Encapsulate 'app = Flask(__name__)' in a method. Having a factory can be useful for testing.
# - Add an "helper" endpoint.
# - Change structure of flask app to make it easier to scale the project
# - Have a file containing the ROOT_DIR to use for generating paths for files if needed
# - Improve test complexity and add custom error/exceptions
############################

DATABASE = 'test.db'

app = Flask(__name__)

## Using sqlite as a POC database only
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    ## for POC purposes only lets also check if table 'test' exists, if not lets create it
    c = db.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Test' ''')
    if c.fetchone()[0] != 1:
        c.execute(
            """CREATE TABLE Test(siteID VARCHAR(255), orgID VARCHAR(255), temperature DECIMAL(10, 5), timestamp INTEGER);""")
        ## Set timestamp as index to avoid duplicates and have faster query by timestamp
        c.execute(("""CREATE UNIQUE INDEX idx_timestamp ON test (timestamp);"""))
    db.commit()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/temp_attributes')
def get_temp_attributes():
    return Response(json.dumps(temp_attributes), mimetype='application/json')

@app.route('/toohotornot')
def get_toohotornot():
    siteId = request.args.get('siteId', -1)  ## todo validate siteID
    if siteId == -1:
        return Response(
            json.dumps({'error': "Missing 'SiteId' attribute."}),
            status=400,
        )
    ## hardcoding orgId for POC purposes, both ids should be given to avoid issues with data retrieval.
    orgId = 'alphacorp'
    ## in order for this to scale the database connection should not be shared from the Flask app, this is just for
    # this POC in order to avoid having many connections
    eval = TempEvaluator(db=get_db()).eval_temp(siteId=siteId, orgId=orgId)
    return Response(json.dumps({'eval' : eval}), mimetype='application/json')

@app.route('/temperature', methods=['POST'])
def post_temperature():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        return Response(
            json.dumps({'message': 'Unsupported media type'}),
            status=415,
        )
    body = request.get_json()
    errors = SchemaValidator.eval(request_json=body)
    if len(errors) > 0:
        return Response(
            json.dumps({'message': errors}),
            status=400,
        )
    db = get_db()
    c = db.cursor()
    try:
        insert_query = f"""INSERT INTO Test
                                  (siteId, orgId, temperature, timestamp) 
                                   VALUES 
                                  ('{body['siteId']}','{body['orgId']}','{body['temperature']}','{body['timestamp']}')"""
        count = c.execute(insert_query)
        db.commit()
    except Exception as e:
        return Response(
            json.dumps({'message': 'Error saving data to database.'}),
            status=500,
        )

    return Response(json.dumps({'status': 'Success!'}), mimetype='application/json')


class SchemaValidator:
    """Class responsible for validating json schemas."""
    @staticmethod
    def eval(request_json={}):
        """Static method that evaluates json schemas.

        Args:
            request_json (dict): Request json data

        Returns:
            list: A list with errors caught.
        """
        errors = []
        if request_json == {} or request_json == None:
            errors.append("Missing JSON data")
            return errors

        if not isinstance(request_json, dict):
            errors.append("Invalid data format")
            return errors

        for attr in temp_attributes:
            try:
                if attr not in request_json.keys():
                    errors.append(f'Attribute {attr} is missing')
            except Exception as e:
                errors.append(f'Attribute {attr} is missing')
        return errors


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=9000)
