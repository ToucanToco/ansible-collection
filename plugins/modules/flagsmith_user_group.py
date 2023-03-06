#!/usr/bin/python

from http import HTTPStatus

import requests
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.payload import sanitize_payload
from ..module_utils.flagsmith import get_organisation_ids_from_names

ORGANISATION_PERMISSIONS_FIELDS = {
    "permissions": {"required": False, "type": "list", "elements": "str"},
}

PROJECT_PERMISSIONS_FIELDS = {
    "permissions": {"required": False, "type": "list", "elements": "str"},
}

PERMISSIONS_FIELDS = {
    "organisation": {"required": False, "type": "dict", "options": ORGANISATION_PERMISSIONS_FIELDS},
    "projects":      {"required": False, "type": "dict", "options": PROJECT_PERMISSIONS_FIELDS},
}

USER_GROUP_FIELDS = {
    "api_key":           {"required": True, "type": "str", "no_log": True},
    "base_url":          {"required": True, "type": "str"},
    "state":             {"required": True, "choices": ["present", "absent"], "type": "str"},
    "organisation_name": {"required": True, "type": "str"},
    "name":              {"required": True, "type": "str"},
    "is_default":        {"required": False, "type": "bool"},
    "permissions":       {"required": False, "type": "dict", "options": PERMISSIONS_FIELDS},
}


class FlagsmithOrganisationPermissions:
    def __init__(self, module, payload):
        self.module               = module
        self.payload              = payload
        self.api_key              = self.payload.pop("api_key")
        self.base_url             = self.payload.pop("base_url")
        self.organisation_id      = self.payload.pop("organisation_id")
        self.group_id             = self.payload.pop("group_id")
        self.headers              = {"Authorization": f"Token {self.api_key}", "Accept": "application/json"}
        self.id                   = None
        self.retrieved_attributes = None

    def diff_attributes(self):
        """ Update the payload to only have the diff between the wanted and the existing attributes """
        diff_attributes = {}
        for key in self.payload:
            if key not in self.retrieved_attributes or self.retrieved_attributes[key] != self.payload[key]:
                diff_attributes[key] = self.payload[key]

        self.payload = diff_attributes

    def create(self):
        """ Create a new user_group org permissions"""
        data={**self.payload, "group": self.group_id}
        resp = requests.post(f"{self.base_url}/organisations/{self.organisation_id}/user-group-permissions/", headers=self.headers, json=data)
        if resp.status_code == HTTPStatus.CREATED:
            return True
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing user_group org permissions"""
        self.diff_attributes()
        if not self.payload:
            self.module.exit_json(changed=False)

        resp = requests.patch(f"{self.base_url}/organisations/{self.organisation_id}/user-group-permissions/{self.id}/", headers=self.headers, json={**self.payload, "group": self.group_id})

        if resp.status_code == HTTPStatus.OK:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def retrieve_id(self):
        """ Retrieve the id of the user_group org permissions if it exists """
        response = requests.get(f"{self.base_url}/organisations/{self.organisation_id}/user-group-permissions?group={self.group_id}", headers=self.headers)
        json_object = response.json()

        if len(json_object) != 0 and type(json_object) is list:
            self.id = json_object[0]['id']
            self.retrieved_attributes = {
                "permissions": json_object[0]['permissions'],
            }

    def manage(self):
        """ Manage the state of a the org permissions """

        self.retrieve_id()

        if not self.id:
            self.create()
        else:
            self.update()

class FlagsmithPermissions:
    def __init__(self, module, payload):
        self.module               = module
        self.payload              = payload
        self.api_key              = self.payload.pop("api_key")
        self.base_url             = self.payload.pop("base_url")
        self.organisation_id      = self.payload.pop("organisation_id")
        self.group_id             = self.payload.pop("group_id")
        self.headers              = {"Authorization": f"Token {self.api_key}", "Accept": "application/json"}
        self.id                   = None
        self.retrieved_attributes = None

    def diff_attributes(self):
        """ Update the payload to only have the diff between the wanted and the existing attributes """
        diff_attributes = {}
        for key in self.payload:
            if key not in self.retrieved_attributes or self.retrieved_attributes[key] != self.payload[key]:
                diff_attributes[key] = self.payload[key]

        self.payload = diff_attributes

    def create(self):
        """ Create a new user_group org permissions"""
        data={**self.payload, "group": self.group_id}
        resp = requests.post(f"{self.base_url}/organisations/{self.organisation_id}/user-group-permissions/", headers=self.headers, json=data)
        if resp.status_code == HTTPStatus.CREATED:
            return True
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing user_group org permissions"""
        self.diff_attributes()
        if not self.payload:
            self.module.exit_json(changed=False)

        resp = requests.patch(f"{self.base_url}/organisations/{self.organisation_id}/user-group-permissions/{self.id}/", headers=self.headers, json={**self.payload, "group": self.group_id})

        if resp.status_code == HTTPStatus.OK:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def retrieve_id(self):
        """ Retrieve the id of the user_group org permissions if it exists """
        response = requests.get(f"{self.base_url}/organisations/{self.organisation_id}/user-group-permissions?group={self.group_id}", headers=self.headers)
        json_object = response.json()

        if len(json_object) != 0 and type(json_object) is list:
            self.id = json_object[0]['id']
            self.retrieved_attributes = {
                "permissions": json_object[0]['permissions'],
            }

    def manage(self):
        """ Manage the state of a the org permissions """

        self.retrieve_id()

        if not self.id:
            self.create()
        else:
            self.update()


class FlagsmithUserGroup:
    def __init__(self, module):
        self.module               = module
        self.payload              = module.params
        self.api_key              = self.payload.pop("api_key")
        self.base_url             = self.payload.pop("base_url")
        self.organisation_name    = self.payload.pop("organisation_name")
        self.state                = self.payload.pop("state")
        self.permissions          = self.payload.pop("permissions")
        self.headers              = {"Authorization": f"Token {self.api_key}", "Accept": "application/json"}
        self.id                   = None
        self.organisation_id      = None
        self.retrieved_attributes = None
        self.changed = False

        self.payload = sanitize_payload(self.payload)

    def retrieve_id(self, api_url):
        """ Retrieve the id of a user_group if it exists """
        response = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["results"]:
            if item["name"] == self.payload["name"]:
                self.id = item["id"]
                self.retrieved_attributes = {
                    "name":      item["name"],
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
            self.changed = True
            self.id = resp.json()["id"]
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing user_group """
        self.diff_attributes()
        if not self.payload:
            return  # no changes to be made

        resp = requests.patch(f"{self.base_url}/organisations/{self.organisation_id}/groups/{self.id}/", headers=self.headers, json=self.payload)

        if resp.status_code == HTTPStatus.OK:
            self.changed = True
        else:
            self.module.fail_json(msg=resp.content)

    def delete(self):
        """ Delete an existing user_group """
        resp = requests.delete(f"{self.base_url}/organisations/{self.organisation_id}/groups/{self.id}/", headers=self.headers)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            self.changed = True
            self.module.exit_json(changed=self.changed)
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

            if self.permissions is not None:
                if self.permissions["organisation"] is not None:
                    organisation_permissions_payload = {
                        "api_key":         self.api_key,
                        "base_url":        self.base_url,
                        "organisation_id": self.organisation_id,
                        "group_id":        self.id,
                        "permissions":     [] if self.permissions["organisation"]["permissions"] is None else self.permissions["organisation"]["permissions"],
                    }
                    organisation_permissions = FlagsmithOrganisationPermissions(self.module, organisation_permissions_payload)
                    organisation_permissions.manage()

            self.module.exit_json(changed=self.changed)

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
