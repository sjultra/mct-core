import os
import requests
import time

class TerraformCloudAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.api_url = 'https://app.terraform.io/api/v2/'
        self.project_id = None
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/vnd.api+json'
        }

    def project_exists(self, org_name, project_name):
        url = f'{self.api_url}organizations/{org_name}/projects'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            workspaces = response.json()['data']
            for workspace in workspaces:
                if workspace['attributes']['name'] == project_name:
                    self.project_id = workspace['id']
                    return True
        return False

    def create_project(self, org_name, project_name):
        data = {
            "data": {
                "attributes": {
                "name": project_name
                },
                "type": "projects"
            }
        }
        url = f'{self.api_url}organizations/{org_name}/projects'
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            print(f'Created project {project_name}')
            return True
        else:
            print(f'Error creating project {project_name}: {response.text}')
            return False

    def workspace_exists(self, org_name, project_name, workspace_name):
        url = f'{self.api_url}organizations/{org_name}/workspaces'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            workspaces = response.json()['data']
            for workspace in workspaces:
                if workspace['attributes']['name'] == workspace_name:
                    print("Workspace:", workspace_name, "already exists")
                    return True
        return False

    def create_workspace(self, org_name, project_name, workspace_name):
        data = {
            'data': {
                'type': 'workspaces',
                'attributes': {
                    'name': workspace_name,
                    'auto-apply': True,
                    'terraform_version': '1.0.0',
                    'working-directory': ''
                },
                "relationships": {
                    "project": {
                        "data": {
                            "type": "projects",
                            "id": self.project_id
                        }
                    }
                }
            }
        }
        url = f'{self.api_url}organizations/{org_name}/workspaces'
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            print(f'Created workspace {workspace_name} in project {project_name}')
            return True
        else:
            print(f'Error creating workspace {workspace_name} in project {project_name}: {response.text}')
            return False

    def create_project_and_workspace(self, org_name, project_name, workspace_name):
        if not self.project_exists(org_name, project_name):
            self.create_project(org_name, project_name)
            self.project_exists(org_name, project_name)
        if not self.workspace_exists(org_name, project_name, workspace_name):
            self.create_workspace(org_name, project_name, workspace_name)


