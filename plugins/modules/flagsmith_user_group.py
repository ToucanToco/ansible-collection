#!/usr/bin/python

from http import HTTPStatus

import requests
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.payload import sanitize_payload
from ..module_utils.flagsmith import get_organisation_ids_from_names

USER_GROUP_FIELDS = {
    "api_key":           {"required": True, "type": "str", "no_log": True},
    "base_url":          {"required": True, "type": "str"},
    "state":             {"required": True, "choices": ["present", "absent"], "type": "str"},
    "organisation_name": {"required": True, "type": "str"},
    "name":              {"required": True, "type": "str"},
    "is_default":        {"required": False, "type": "bool"},
}


class FlagsmithUserGroup:
    def __init__(self, module):
        self.module               = module
        self.payload              = module.params
        self.api_key              = self.payload.pop("api_key")
        self.base_url             = self.payload.pop("base_url")
        self.organisation_name    = self.payload.pop("organisation_name")
        self.state                = self.payload.pop("state")
        self.headers              = {"Authorization": f"Token {self.api_key}", "Accept": "application/json"}
        self.id                   = None
        self.organisation_id      = None
        self.retrieved_attributes = None

        self.payload = sanitize_payload(self.payload)

    def retrieve_id(self, api_url):
        """ Retrieve the id of a user_group if it exists """
        response = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["results"]:
            if item["name"] == self.payload["name"]:
                self.id = item["id"]
                self.retrieved_attributes = {
                    "users":      item["users"],
                    "is_default": item["is_default"],
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
        """ Create a new user_group """
        resp = requests.post(f"{self.base_url}/organisations/{self.organisation_id}/groups/", headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing user_group """
        self.diff_attributes()
        if not self.payload:
            self.module.exit_json(changed=False)

        resp = requests.patch(f"{self.base_url}/organisations/{self.organisation_id}/groups/{self.id}/", headers=self.headers, json=self.payload)

        if resp.status_code == HTTPStatus.OK:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def delete(self):
        """ Delete an existing user_group """
        resp = requests.delete(f"{self.base_url}/organisations/{self.organisation_id}/groups/{self.id}/", headers=self.headers)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def manage(self):
        """ Manage state of a user_group """
        organisation_ids = get_organisation_ids_from_names(self.base_url, self.headers, [self.organisation_name])

        if len(organisation_ids) == 0:
            self.module.fail_json(msg="Organisation was not found")
        else:
            self.organisation_id = organisation_ids[0]

        self.retrieve_id(f"{self.base_url}/organisations/{self.organisation_id}/groups/")

        if self.state == "present":
            if not self.id:
                self.create()
            else:
                self.update()
        elif self.state == "absent":
            if not self.id:
                self.module.exit_json(changed=False, msg="No user_group to delete")
            else:
                self.delete()


def main():
    module = AnsibleModule(
      argument_spec=USER_GROUP_FIELDS,
      supports_check_mode=True,
    )

    user_group_object = FlagsmithUserGroup(module)

    if not module.check_mode:
        user_group_object.manage()
    else:
        return module.exit_json(changed=False)


if __name__ == "__main__":
    main()
