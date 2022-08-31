"""
Fetch SLA for monitors
"""

#!/usr/bin/python

import urllib

import requests
from ansible.module_utils.basic import AnsibleModule
from requests.models import PreparedRequest

from ..module_utils.payload import sanitize_payload

API_MONITORS_BASE_URL = "https://betteruptime.com/api/v2/monitors"

MONITOR_SLA_FIELDS = {
    "api_key": {"required": True, "type": "str", "no_log": True},
    "url":     {"required": True, "type": "str"},
    "from":    {"required": False, "type": "str"},
    "to":      {"required": False, "type": "str"},
}



class BetterUptimeMonitorSLA:
    def __init__(self, module):
        self.module  = module
        self.payload = module.params
        self.headers = {"Authorization": f"Bearer {self.payload.pop('api_key')}"}

        self.monitor_url            = self.payload.pop('url')
        self.monitor_id             = None
        self.monitor_attributes     = None
        self.monitor_sla_attributes = None

        self.payload = sanitize_payload(self.payload)

    def retrieve_monitor_id(self, api_url):
        """ Retrieve the id of a monitor if it exists """
        response = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            if item["attributes"] and item["attributes"]["url"] == self.monitor_url:
                self.monitor_id = item["id"]
                self.monitor_attributes = item["attributes"]
                return

        if json_object["pagination"]["next"] is not None:
            self.retrieve_monitor_id(json_object["pagination"]["next"])


    def get_sla(self):
        """ Retrieve the SLA"""
        req = PreparedRequest()
        req.prepare_url(f"{API_MONITORS_BASE_URL}/{self.monitor_id}/sla", self.payload)

        response = requests.get(req.url, headers=self.headers)
        if response.status_code != 200:
            self.module.fail_json(msg=response.json())

        self.monitor_sla_attributes = response.json()["data"]["attributes"]

    def manage(self):
        """ Manage monitor SLA retrieval """
        self.retrieve_monitor_id(f"{API_MONITORS_BASE_URL}?url={urllib.parse.quote(self.monitor_url)}")

        if self.monitor_id is None:
            self.module.fail_json(msg="Monitor no found")

        self.get_sla()
        result = {**self.monitor_sla_attributes, "monitor_creation_date":  self.monitor_attributes["created_at"]}

        self.module.exit_json(**result)



def main():
    module = AnsibleModule(
      argument_spec=MONITOR_SLA_FIELDS,
      supports_check_mode=True,
    )

    monitor_sla_object = BetterUptimeMonitorSLA(module)

    if not module.check_mode:
        monitor_sla_object.manage()
    else:
        return module.exit_json(changed=False)


if __name__ == "__main__":
    main()
