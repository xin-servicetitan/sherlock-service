from db_actions import DatabaseHandler
from teamcity_data_pull import TeamCityAPI
import os
import json

def main():
    # Database Connection
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

    # TeamCity API
    base_url = 'https://teamcity.st.dev'
    bearer_token = os.environ.get('BEARER_TOKEN')
    oauth2_proxy = os.environ.get('OAUTH2_PROXY')
    tc_api = TeamCityAPI(base_url, bearer_token, oauth2_proxy)

    build_id_list = tc_api.get_builds_list_for_past_5minutes()
    print("build id list", build_id_list)

    data = tc_api.get_all_detials_for_build('4116731')
    formatted_json = json.dumps(data, indent=4)
    sql_statements = tc_api.get_test_execution_sqls(data)
    print("-------")
    for t in sql_statements:
    #    db_handler.execute_query(t)
        print(t)
    print("-------")
    #sql = tc_api.get_builds_sql(data)
    #print("-------")
    #print(sql)
    #print("-------")
    #res = db_handler.execute_query(sql)
    #print(res)
    #print("-------")
    


    # build_data = tc_api.get_builds_data()
    # db_handler.execute_query(your_query_here)

    db_handler.close()

if __name__ == "__main__":
    main()

