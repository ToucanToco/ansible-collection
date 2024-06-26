#!/usr/bin/python

import urllib
from http import HTTPStatus

import requests
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.payload import sanitize_payload

API_MONITORS_BASE_URL = "https://betteruptime.com/api/v2/monitors"
API_POLICIES_BASE_URL = "https://betteruptime.com/api/v2/policies"

MONITOR_FIELDS = {
    "api_key":               {"required": True, "type": "str", "no_log": True},
    "url":                   {"required": True, "type": "str"},
    "state":                 {"required": True, "choices": ["present", "absent"], "type": "str"},
    "monitor_type":          {
      "required":            False,
      "choices":             [
        "expected_status_code",
        "imap",
        "keyword",
        "keyword_absence",
        "ping",
        "pop",
        "smtp",
        "status",
        "tcp",
        "udp",
      ],
      "type":                "str"
    },
    "metadata":              {"required": False, "type": "list", "elements": "dict"},
    "expected_status_codes": {"required": False, "type": "list", "elements": "int"},
    "request_headers":       {"required": False, "type": "list", "elements": "dict"},
    "domain_expiration":     {"required": False, "type": "int"},
    "ssl_expiration":        {"required": False, "type": "int"},
    "policy_name":           {"required": False, "type": "str"},
    "follow_redirects":      {"required": False, "type": "bool"},
    "required_keyword":      {"required": False, "type": "str"},
    "call":                  {"required": False, "type": "bool", "default": False},
    "sms":                   {"required": False, "type": "bool", "default": False},
    "email":                 {"required": False, "type": "bool", "default": True},
    "push":                  {"required": False, "type": "bool", "default": False},
    "team_wait":             {"required": False, "type": "int"},
    "paused":                {"required": False, "type": "bool", "default": False},
    "port":                  {"required": False, "type": "str"},
    "regions":               {"required": False, "type": "list", "elements": "str"},
    "monitor_group_id":      {"required": False, "type": "str"},
    "pronounceable_name":    {"required": False, "type": "str"},
    "recovery_period":       {"required": False, "type": "int"},
    "verify_ssl":            {"required": False, "type": "bool"},
    "check_frequency":       {"required": False, "type": "int", "default": 300},
    "confirmation_period":   {"required": False, "type": "int", "default": 120},
    "http_method":           {"required": False, "type": "str"},
    "request_timeout":       {"required": False, "type": "int"},
    "request_body":          {"required": False, "type": "str"},
    "auth_username":         {"required": False, "type": "str"},
    "auth_password":         {"required": False, "type": "str", "no_log": True},
    "maintenance_from":      {"required": False, "type": "str"},
    "maintenance_to":        {"required": False, "type": "str"},
    "maintenance_timezone":  {"required": False, "type": "str"},
    "remember_cookies":      {"required": False, "type": "bool"},
    "checks_version":        {"required": False, "type": "str"},
    "ip_version":            {"required": False, "type": "str"},
}

MONITOR_REQUIRED_IF = [
    ("state", "present", ("monitor_type",)),
    ("monitor_type", "tcp", ("port",)),
    ("monitor_type", "udp", ("port", "required_keyword")),
    ("monitor_type", "expected_status_code", ("expected_status_codes",)),
    ("monitor_type", "keyword", ("required_keyword",)),
    ("monitor_type", "keyword_absence", ("required_keyword",)),
]


class BetterUptimeEscalationPolicy:
    def __init__(self, headers, name):
        self.headers = headers
        self.name    = name
        self.id      = None

    def retrieve_id(self):
        """ Retrieve the id of an escalation policy if it exists """
        response = requests.get(API_POLICIES_BASE_URL, headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            if item["attributes"] and item["attributes"]["name"] == self.name:
                self.id = item["id"]
                return

class BetterUptimeMonitor:
    def __init__(self, module):
        self.module               = module
        self.payload              = module.params
        self.api_key              = self.payload.pop("api_key")
        self.metadata             = self.payload.pop("metadata")
        self.state                = self.payload.pop("state")
        self.policy_name          = self.payload.pop("policy_name")
        self.headers              = {"Authorization": f"Bearer {self.api_key}"}
        self.id                   = None
        self.retrieved_attributes = None

        self.payload = sanitize_payload(self.payload)

    def retrieve_id(self, api_url):
        """ Retrieve the id of a monitor if it exists """
        response = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            if item["attributes"] and item["attributes"]["url"] == self.payload["url"]:
                if  ("port" not in self.payload and ("port" not in item["attributes"] or item["attributes"]["port"] is None)) or\
                    ("port" in self.payload and "port" in item["attributes"] and item["attributes"]["port"] == self.payload["port"]):
                    self.id = item["id"]
                    self.retrieved_attributes = item["attributes"]
                    return

        if json_object["pagination"]["next"] is not None:
            self.retrieve_id(json_object["pagination"]["next"])

    def retrieve_policy_id(self):
        """ Retreve the policy id """
        if self.policy_name is not None:
            policy = BetterUptimeEscalationPolicy(self.headers, self.policy_name)
            policy.retrieve_id()
            self.payload["policy_id"] = policy.id

    def diff_attributes(self):
        """ Update the payload to only have the diff between the wanted and the existed attributes """
        diff_attributes = {}
        for key in self.payload:
            if key == "request_headers":
                same = all(i in [{"name": j["name"], "value": j["value"]} for j in self.retrieved_attributes[key]] for i in self.payload[key])
                if not same or len(self.retrieved_attributes[key]) != len(self.payload[key]):
                    destroyed_headers = [{"id": i["id"], "_destroy": True} for i in self.retrieved_attributes[key]]
                    self.payload[key] = self.payload[key] + destroyed_headers
                    diff_attributes[key] = self.payload[key]
            elif key not in self.retrieved_attributes or self.retrieved_attributes[key] != self.payload[key]:
                diff_attributes[key] = self.payload[key]

        self.payload = diff_attributes

    def create(self):
        """ Create a new montitor """
        resp = requests.post(API_MONITORS_BASE_URL, headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing montitor """
        self.diff_attributes()
        if not self.payload:
            self.module.exit_json(changed=False)

        resp = requests.patch(f"{API_MONITORS_BASE_URL}/{self.id}", headers=self.headers, json=self.payload)

        if resp.status_code == HTTPStatus.OK:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def delete(self):
        """ Delete an existing montitor """
        resp = requests.delete(f"{API_MONITORS_BASE_URL}/{self.id}", headers=self.headers)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            self.module.exit_json(changed=True)
        else:
            self.module.fail_json(msg=resp.content)

    def manage_monitor(self):
        """ Manage state of a montitor """
        self.retrieve_policy_id()
        self.retrieve_id(f"{API_MONITORS_BASE_URL}?url={urllib.parse.quote(self.payload['url'])}")

        if self.state == "present":
            if not self.id:
                self.create()
            else:
                self.update()
        elif self.state == "absent":
            if not self.id:
                self.module.exit_json(changed=False, msg="No test to delete with the specified url")
            else:
                self.delete()

def main():
    module = AnsibleModule(
      argument_spec=MONITOR_FIELDS,
      supports_check_mode=True,
      required_if=MONITOR_REQUIRED_IF
    )

    monitor_object = BetterUptimeMonitor(module)

    if not module.check_mode:
        monitor_object.manage_monitor()
    else:
        return module.exit_json(changed=False)


if __name__ == "__main__":
    main()
