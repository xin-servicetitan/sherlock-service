from flask import Flask, request, jsonify
from db_actions import DatabaseHandler
from teamcity_data_pull import TeamCityAPI
import os
import json

app = Flask(__name__)

# Initialize TeamCityAPI with your credentials
base_url = 'https://teamcity.st.dev'
bearer_token = os.environ.get('BEARER_TOKEN')
oauth2_proxy = os.environ.get('OAUTH2_PROXY')
tc_api = TeamCityAPI(base_url, bearer_token, oauth2_proxy)

# Initialize DatabaseHandler
password = os.environ.get('PASSWORD')
connection_string = (
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=testdb-xin.database.windows.net,1433;'
    'DATABASE=testdb_xin;'
    'UID=xin-test;'
    f'PWD={password};'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)
db_handler = DatabaseHandler(connection_string)
db_handler.connect()

@app.route('/get-build-details', methods=['GET'])
def get_build_details():
    build_id = request.args.get('build_id')
    if not build_id:
        return jsonify({'error': 'Missing build_id parameter'}), 400
    try:
        build_details = tc_api.get_build_details(build_id)
        return jsonify(build_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/insert-build-details', methods=['POST'])
def insert_build_details():
    print("Received request for /insert-build-details")

    data = request.json
    print("Request JSON Data:")
    print(json.dumps(data, indent=4))

    build_id = data.get('build_id')
    if not build_id:
        print("Error: Missing build_id in the request body")
        return jsonify({'error': 'Missing build_id in the request body'}), 400

    try:
        print(f"Fetching build details for build_id: {build_id}")
        build_details = tc_api.get_all_detials_for_build(build_id)
        print("Build Details Retrieved:")
        print(json.dumps(build_details, indent=4))

        print("Generating SQL for build details insertion")
        build_sql = tc_api.get_builds_sql(build_details)
        print(f"Executing SQL: {build_sql}")
        db_handler.execute_query(build_sql)
        print("Build details inserted successfully")

        print(f"Fetching test occurrences for build_id: {build_id}")
        tests_sql = tc_api.get_test_execution_sqls(build_details)
        print(f"Executing SQL for test occurrence: {tests_sql}")
        for test_sql in tests_sql:
            print(f"Executing SQL for test occurrence: {test_sql}")
            db_handler.execute_query(test_sql)
            print("Test occurrence inserted successfully")

        return jsonify({'message': 'Data inserted successfully'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

