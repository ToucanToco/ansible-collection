#!/usr/bin/python

from http import HTTPStatus

import requests
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.payload import sanitize_payload
from ..module_utils.flagsmith import get_project_ids_from_names

import collections

import ast

import json

SEGMENT_FIELDS = {
    "api_key":         {"required": True, "type": "str", "no_log": True},
    "base_url":        {"required": True, "type": "str"},
    "state":           {"required": True, "choices": ["present", "absent"], "type": "str"},
    "project_name":    {"required": True, "type": "str"},
    "name":            {"required": True, "type": "str"},
    "rules":           {"required": True, "type": "str"},
}

class FlagsmithSegmentRule:
    def __init__(self, module):
        self.module               = module
        self.payload              = module.params
        self.api_key              = self.payload.pop("api_key")
        self.base_url             = self.payload.pop("base_url")
        self.project_name         = self.payload.pop("project_name")
        self.state                = self.payload.pop("state")
        self.headers              = {"Authorization": f"Api-Key {self.api_key}", "Accept": "application/json"}
        self.id                   = None
        self.project_id           = None
        self.retrieved_attributes = None
        self.env_api_key          = None

        self.payload = sanitize_payload(self.payload)
        if 'initial_value' in self.payload:
            # Transform to a valid json string if initial_value is a dict
            try:
                typed_initial_value = ast.literal_eval(self.payload['initial_value'])
                if type(typed_initial_value) is dict:
                    self.payload['initial_value'] = json.dumps(typed_initial_value)
            except ValueError:
                pass

    def retrieve_id(self, api_url):
        """Retrieve the ID of a segment if it exists."""
        try:
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()
            for item in data.get("results", []):
                if item["name"] == self.payload["name"]:
                    self.id = item["id"]
                    return
        except requests.exceptions.RequestException as e:
            self.module.fail_json(msg=f"Segment was not found, {self.payload['name']}, error: {e}")

    def update(self):
        """ Update an existing segment """
        # self.diff_attributes()
        if not self.payload:
            self.module.exit_json(changed=False)
        rule_update_resp = requests.patch(f"{self.base_url}/projects/{self.project}/segments/{self.id}/", headers=self.headers, json=self.payload)

        if rule_update_resp.status_code == HTTPStatus.OK:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=f"segment update failed. {rule_update_resp.status_code} {rule_update_resp.content} \n  Uri: {rule_update_resp.url} \n Sent payload: {self.payload}")

    def manage(self):
        self.payload["name"]=f"{self.payload['name'].lower()}"
        if self.payload['name']=="none" or self.payload["name"] == "custom":
            self.module.exit_json(skipped=True)
        self.payload['rules'] = self.payload['rules'].replace("'", '"')
        self.payload['rules'] = json.loads(self.payload['rules'])
        
        """ Manage state of a segment """
        project_ids = get_project_ids_from_names(self.base_url, self.headers, [self.project_name])
        
        if len(project_ids) == 0:
            self.module.fail_json(msg=f"Project was not found, {project_ids}")
        else:
            self.project = project_ids[0]
            self.payload["project"] = self.project
        self.retrieve_id(f"{self.base_url}/projects/{self.project}/segments/?search={self.payload['name']}")
        
        if self.state == "present" and self.id:
            self.update()
        else:
            self.module.fail_json(msg=f"Segment was not found, {self.payload['name']}")
            

def main():
    module = AnsibleModule(
      argument_spec=SEGMENT_FIELDS,
      supports_check_mode=True,
    )

    segment_rule_object = FlagsmithSegmentRule(module)

    if not module.check_mode:
        segment_rule_object.manage()
    else:
        return module.exit_json(changed=False)


if __name__ == "__main__":
    main()
