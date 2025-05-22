#!/usr/bin/python

from http import HTTPStatus

import requests
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.payload import sanitize_payload
from ..module_utils.flagsmith import get_project_ids_from_names

import random

TAG_FIELDS = {
    "api_key":      {"required": True, "type": "str", "no_log": True},
    "base_url":     {"required": True, "type": "str"},
    "state":        {"required": True, "choices": ["present", "absent"], "type": "str"},
    "project_name": {"required": True, "type": "str"},
    "label":        {"required": True, "type": "str"},
    "color":        {"required": False, "type": "str"},
    "description":  {"required": False, "type": "str"},
}

class FlagsmithTag:
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

        self.payload = sanitize_payload(self.payload)

    def retrieve_id(self, api_url):
        """ Retrieve the id of a tag if it exists """
        response = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["results"]:
            if item["label"] == self.payload["label"]:
                self.id = item["id"]
                self.retrieved_attributes = {
                    "label":       item["label"],
                    "color":       item["color"],
                    "description": item["description"]
                }
                return

        if json_object["next"] is not None:
            self.retrieve_id(json_object["next"])

    def diff_attributes(self):
        """ Update the payload to only have the diff between the wanted and the existing attributes """
        diff_attributes = {}
        for key in self.payload:
            if key not in self.retrieved_attributes or self.retrieved_attributes[key] != self.payload[key]:
                diff_attributes[key] = self.payload[key]

        self.payload = diff_attributes

    def create(self):
        """ Create a new tag """
        resp = requests.post(f"{self.base_url}/projects/{self.project_id}/tags/", headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing tag """
        self.diff_attributes()
        if not self.payload:
            self.module.exit_json(changed=False)

        resp = requests.patch(f"{self.base_url}/projects/{self.project_id}/tags/{self.id}/", headers=self.headers, json=self.payload)

        if resp.status_code == HTTPStatus.OK:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def delete(self):
        """ Delete an existing tag """
        resp = requests.delete(f"{self.base_url}/projects/{self.project_id}/tags/{self.id}/", headers=self.headers)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def manage(self):
        """ Manage state of a tag """

        project_ids = get_project_ids_from_names(self.base_url, self.headers, [self.project_name])
        if len(project_ids) == 0:
            self.module.fail_json(msg=f"project {self.project_name} not found")
        else:
            self.project_id = project_ids[0]

        self.retrieve_id(f"{self.base_url}/projects/{self.project_id}/tags/")

        if self.state == "present":
            if not self.id:
                if 'color' not in self.payload:
                    self.payload['color'] = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                self.create()
            else:
                self.update()
        elif self.state == "absent":
            if not self.id:
                self.module.exit_json(changed=False, msg="No tag to delete")
            else:
                self.delete()


def main():
    module = AnsibleModule(
      argument_spec=TAG_FIELDS,
      supports_check_mode=True,
    )

    tag_object = FlagsmithTag(module)

    if not module.check_mode:
        tag_object.manage()
    else:
        return module.exit_json(changed=False)


if __name__ == "__main__":
    main()
