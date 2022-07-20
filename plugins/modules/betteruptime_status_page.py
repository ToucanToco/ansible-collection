#!/usr/bin/python

import requests

from ansible.module_utils.basic import AnsibleModule

API_STATUS_PAGES_BASE_URL = "https://betteruptime.com/api/v2/status-pages"

STATUS_PAGES_FIELDS = {
    "api_key":                       {"required": True, "type": "str", "no_log": True},
    "state":                         {"required": True, "type": "str", "choices": ["present", "absent"]},
    "subdomain":                     {"required": True, "type": "str"},
    "company_name":                  {"required": False, "type": "str", "default": "ToucanToco"},
    "company_url":                   {"required": False, "type": "str", "default": "https://www.toucantoco.com"},
    "contact_url":                   {"required": False, "type": "str"},
    "logo_url":                      {"required": False, "type": "str"},
    "timezone":                      {"required": False, "type": "str", "default": "Paris"},
    "custom_domain":                 {"required": False, "type": "str"},
    "custom_css":                    {"required": False, "type": "str"},
    "google_analytics_id":           {"required": False, "type": "str"},
    "min_incident_length":           {"required": False, "type": "int"},
    "announcement":                  {"required": False, "type": "str"},
    "announcement_embed_visible":    {"required": False, "type": "bool"},
    "announcement_embed_custom_css": {"required": False, "type": "str"},
    "announcement_embed_link":       {"required": False, "type": "str"},
    "subscribable":                  {"required": False, "type": "bool"},
    "hide_from_search_engines":      {"required": False, "type": "bool"},
    "password_enabled":              {"required": False, "type": "bool"},
    "password":                      {"required": False, "type": "str", "no_log": True},
    "history":                       {"required": False, "type": "int"},
}

STATUS_PAGE_IF = [
]


class BetterUptimeStatusPage:
    def __init__(self, module):
        self.module               = module
        self.payload              = module.params
        self.api_key              = self.payload.pop("api_key")
        self.state                = self.payload.pop("state")
        self.headers              = {"Authorization": f"Bearer {self.api_key}"}
        self.id                   = None
        self.retrieved_attributes = None

        self.sanitize_payload()

    def sanitize_payload(self):
        """ Remove attributes set to None """
        self.payload = {k:v for (k,v) in self.payload.items() if v is not None}

    def diff_attributes(self):
        """ Update the payload to only have the diff between the wanted and the existed attributes """
        self.payload = {k:v for (k,v) in self.payload.items() if (k,v) not in self.retrieved_attributes.items()}

    def retrieve_id(self, api_url):
        """ Retrieve the id of a status page if it exists """
        response = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            if item["attributes"] and item["attributes"]["subdomain"] == self.payload["subdomain"]:
                self.id = item["id"]
                self.retrieved_attributes = item["attributes"]
                return

        if json_object["pagination"]["next"] is not None:
            self.retrieve_id(json_object["pagination"]["next"])

    def create(self):
        """ Create a new status page """
        resp = requests.post(API_STATUS_PAGES_BASE_URL, headers=self.headers, json=self.payload)
        if resp.status_code == 201:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing status page """
        self.diff_attributes()
        if not self.payload:
            self.module.exit_json(changed=False)

        resp = requests.patch(f"{API_STATUS_PAGES_BASE_URL}/{self.id}", headers=self.headers, json=self.payload)
        if resp.status_code == 200:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def delete(self):
        """ Delete a status page """
        resp = requests.delete(f"{API_STATUS_PAGES_BASE_URL}/{self.id}", headers=self.headers)
        if resp.status_code == 204:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def manage_status_page(self):
        """ Manage state of a status page """
        self.retrieve_id(API_STATUS_PAGES_BASE_URL)

        if self.state == "present":
            if not self.id:
                res = self.create()
            else:
                res = self.update()
        elif self.state == "absent":
            if not self.id:
                self.module.exit_json(changed=False, msg="No test to delete with the specified url")
            else:
                res = self.delete()

def main():
    module = AnsibleModule(
      argument_spec=STATUS_PAGES_FIELDS,
      supports_check_mode=True,
      required_if=STATUS_PAGE_IF
    )

    status_page_object = BetterUptimeStatusPage(module)

    if not module.check_mode:
        status_page_object.manage_status_page()
    else:
        return module.exit_json(changed=False)

if __name__ == "__main__":
    main()
