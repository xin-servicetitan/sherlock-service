import requests
import pytz
import json
from urllib.parse import urljoin
from utils import flatten_json
from datetime import datetime, timedelta



class TeamCityAPI:
    def __init__(self, base_url, bearer_token, oauth2_proxy):
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.oauth2_proxy = oauth2_proxy
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}',
            'cookie': f'_oauth2_proxy={self.oauth2_proxy}'
        }

    def get_build_details(self, build_id):
        """
        Fetches details of a specific build using its build ID.
        """
        if not build_id:
            return {}

        relative_path = f'/app/rest/builds/id:{build_id}'
        url = urljoin(self.base_url, relative_path)

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return flatten_json(response.json())

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return {'error': 'HTTP error occurred'}
        except Exception as e:
            print(f"Other error occurred: {e}")
            return {'error': 'An error occurred during the API request'}

    @staticmethod
    def get_last_5minutes():
        timezone = pytz.timezone('US/Pacific')
        now = datetime.now(timezone)
        five_minutes_ago = now - timedelta(minutes=100)

        formatted_time = five_minutes_ago.strftime('%Y%m%dT%H%M%S')
        offset = five_minutes_ago.strftime('%z')
        formatted_time_with_offset = f"{formatted_time}{offset[:-2]}:{offset[-2:]}"

        return formatted_time_with_offset

    def get_builds_list_for_past_5minutes(self):
        time_5mins_ago = self.get_last_5minutes()
        relative_path = f'/app/rest/builds?locator=finishDate:(date:{time_5mins_ago},condition:after),count:10000'
        url = urljoin(self.base_url, relative_path)
        response = requests.get(url, headers=self.headers)
        print(f"Response Status Code: {response.status_code}")
        try:
            builds = response.json()
            """
            {
                "id": 4147437,
                "buildTypeId": "Services_DispatchCenter_Messaging_Merge",
                "number": "163",
                "status": "SUCCESS",
                "state": "finished",
                "href": "/app/rest/builds/id:4147437",
                "webUrl": "https://teamcity.st.dev/viewLog.html?buildId=4147437&buildTypeId=Services_DispatchCenter_Messaging_Merge",
                "finishOnAgentDate": "20240119T205812+0000",
                "matrixConfiguration": {
                    "enabled": false
                }
            }
            """
            build_ids = [build["id"] for build in builds["build"]]
            return build_ids
        except json.JSONDecodeError:
            print("Failed to decode JSON. Invalid response received.")
            return []

    def get_all_detials_for_build(self, build_id):
        """
        Fetches test occurrences for a given build ID.
        """
        print("enter get_test_occurrences_for_build")
        relative_path = f'/app/rest/testOccurrences?locator=build:{build_id},count:1000'
        url = urljoin(self.base_url, relative_path)
        response = requests.get(url, headers=self.headers)

        try:
            response.raise_for_status()  # Will raise an HTTPError for bad requests

            data = response.json()
            res = {}

            count = data.get('count', 0)
            if not count : return {}

            res['count'] = count
            res['ignored'] = data.get('ignored', 0)
            res['failed'] = data.get('failed', 0)
            res['new_failed'] = data.get('new_failed', 0)
            res['muted'] = data.get('muted', 0)
            res['test_occurrence'] = data.get('testOccurrence', [])

            build_detials = self.get_build_details(build_id)
            build_detials.update(res)

            print("exist get_test_occurrences_for_build")
            return build_detials

        except requests.JSONDecodeError:
            print("Failed to decode JSON. Invalid response received.")
            return {}
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return {}
        except Exception as e:
            print(f"Other error occurred: {e}")
            return {}

    def get_all_data_fields_for_build_id(self, build_id):
        test_occurrence_all = tc_api.get_test_occurrences_for_build(build_id)
        
    def get_test_execution_sqls(self, data):
        sqls = []
        build_id = data["id"]

        for test in data.get("test_occurrence", []):
            test_id = test.get("id", "")
            name = test.get("name", "").replace("'", "''")  # Escaping single quotes
            status = test.get("status", "")
            duration = test.get("duration", 0)
            href = test.get("href", "")
            muted = 1 if test.get("muted", False) else 0
            ignored = 1 if test.get("ignored", False) else 0
    
            sql = f"""
                INSERT INTO test_executions (
                    id, name, build_id, duration, status, href, muted, ignored
                ) VALUES (
                    '{test_id}', '{name}', '{build_id}', {duration}, '{status}', '{href}', {muted}, {ignored}
                )
            """
            sqls.append(sql)
    
        return sqls
   
    def get_builds_sql(self, data):
        def convert_date(date_str):
            if date_str:
                return datetime.strptime(date_str, '%Y%m%dT%H%M%S%z').strftime('%Y-%m-%d %H:%M:%S')
            return None
    
        start_time = convert_date(data.get('start_date'))
        end_time = convert_date(data.get('finish_date'))
    
        sql = f"""
        IF EXISTS (SELECT 1 FROM builds WHERE build_id = '{data.get('id')}')
        BEGIN
            UPDATE builds
            SET
                build_type_id = '{data.get('build_type_id')}',
                status = '{data.get('status')}',
                state = '{data.get('state')}',
                href = '{data.get('href')}',
                web_url = '{data.get('web_url')}',
                count = {data.get('count', 0)},
                passed = {data.get('test_occurrences_passed', 0)},
                ignored = {data.get('ignored', 0)},
                failed = {data.get('failed', 0)},
                new_failed = {data.get('new_failed', 0)},
                muted = {data.get('muted', 0)},
                start_time = '{start_time}',
                end_time = '{end_time}',
                build_type_name = '{data.get('build_type_name')}',
                project_name = '{data.get('build_type_project_name')}',
                project_id = '{data.get('build_type_project_id')}',
                agent_name = '{data.get('agent_name')}',
                build_type_description = '{data.get('build_type_description')}'
            WHERE build_id = '{data.get('id')}'
        END
        ELSE
        BEGIN
            INSERT INTO builds (
                build_id,
                build_type_id,
                status,
                state,
                href,
                web_url,
                count,
                passed,
                ignored,
                failed,
                new_failed,
                muted,
                start_time,
                end_time,
                build_type_name,
                project_name,
                project_id,
                agent_name,
                build_type_description
            ) VALUES (
                '{data.get('id')}',
                '{data.get('build_type_id')}',
                '{data.get('status')}',
                '{data.get('state')}',
                '{data.get('href')}',
                '{data.get('web_url')}',
                {data.get('count', 0)},
                {data.get('test_occurrences_passed', 0)},
                {data.get('ignored', 0)},
                {data.get('failed', 0)},
                {data.get('new_failed', 0)},
                {data.get('muted', 0)},
                '{start_time}',
                '{end_time}',
                '{data.get('build_type_name')}',
                '{data.get('build_type_project_name')}',
                '{data.get('build_type_project_id')}',
                '{data.get('agent_name')}',
                '{data.get('build_type_description')}'
            )
        END
        """
        return sql

       
"""
{
    "id": 4116730,
    "build_type_id": "DataScience_CypressDs_Tests_AdPropensity_Api",
    "number": "62",
    "status": "SUCCESS",
    "state": "finished",
    "branch_name": "master",
    "default_branch": true,
    "href": "/app/rest/builds/id:4116730",
    "web_url": "https://teamcity.st.dev/viewLog.html?buildId=4116730&buildTypeId=DataScience_CypressDs_Tests_AdPropensity_Api",
    "status_text": "Tests passed: 6, ignored: 1",
    "build_type_name": "API",
    "build_type_description": "API tests run build",
    "build_type_project_name": "Data Science / Cypress-ds / Tests / ad-propensity",
    "build_type_project_id": "DataScience_CypressDs_Tests_AdPropensity",
    "build_type_href": "/app/rest/buildTypes/id:DataScience_CypressDs_Tests_AdPropensity_Api",
    "build_type_web_url": "https://teamcity.st.dev/viewType.html?buildTypeId=DataScience_CypressDs_Tests_AdPropensity_Api",
    "queued_date": "20240114T100000+0000",
    "start_date": "20240114T100001+0000",
    "finish_date": "20240114T100232+0000",
    "triggered_type": "schedule",
    "triggered_date": "20240114T100000+0000",
    "last_changes_count": 1,
    "last_changes_change_0_id": 5847977,
    "last_changes_change_0_version": "6e336ed7431aef29082417285eca04a078ba520a",
    "last_changes_change_0_username": "33745649+zargaryanlilit",
    "last_changes_change_0_date": "20231219T160141+0000",
    "last_changes_change_0_href": "/app/rest/changes/id:5847977",
    "last_changes_change_0_web_url": "https://teamcity.st.dev/viewModification.html?modId=5847977&personal=false",
    "changes_href": "/app/rest/changes?locator=build:(id:4116730)",
    "revisions_count": 1,
    "revisions_revision_0_version": "6e336ed7431aef29082417285eca04a078ba520a",
    "revisions_revision_0_vcs_branch_name": "refs/heads/master",
    "revisions_revision_0_vcs-root-instance_id": "3259",
    "revisions_revision_0_vcs-root-instance_vcs-root-id": "DataScience_CypressDs_CypressDsVcs4",
    "revisions_revision_0_vcs-root-instance_name": "Cypress DS VCS (4)",
    "revisions_revision_0_vcs-root-instance_href": "/app/rest/vcs-root-instances/id:3259",
    "agent_name": "small-spot-privileged-root-42699",
    "agent_type_id": 110179,
    "test_occurrences_count": 7,
    "test_occurrences_href": "/app/rest/testOccurrences?locator=build:(id:4116730)",
    "test_occurrences_ignored": 1,
    "test_occurrences_passed": 6,
    "artifacts_href": "/app/rest/builds/id:4116730/artifacts/children/",
    "related_issues_href": "/app/rest/builds/id:4116730/relatedIssues",
    "statistics_href": "/app/rest/builds/id:4116730/statistics",
    "finish_on_agent_date": "20240114T100232+0000",
    "matrix_configuration_enabled": false,
    "count": 7,
    "ignored": 1,
    "failed": 0,
    "new_failed": 0,
    "muted": 0,
    "test_occurrence": [
        {
            "id": "build:(id:4116730),id:2000000000",
            "name": "Propensity functional test with invalid request body: Having tenant id as integet should result in bad request",
            "status": "UNKNOWN",
            "ignored": true,
            "href": "/app/rest/testOccurrences/build:(id:4116730),id:2000000000"
        },
        {
            "id": "build:(id:4116730),id:2000000006",
            "name": "Propensity functional test checking score is valid: Send multiitem request and check if scores are from correct values",
            "status": "SUCCESS",
            "duration": 283,
            "href": "/app/rest/testOccurrences/build:(id:4116730),id:2000000006"
        }
    ]
}
"""
