#!/usr/bin/python

from datetime import datetime, timezone
from http import HTTPStatus
import requests

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.payload import sanitize_payload
from ..module_utils.date import validate_date
from ..module_utils.date import compare_date

API_STATUS_PAGES_BASE_URL = "https://betteruptime.com/api/v2/status-pages"

STATUS_PAGE_REPORT_UPDATES_FIELDS = {
    "message":      {"required": True, "type": "str"},
    "published_at": {"required": False, "type": "str"},
}

STATUS_PAGE_REPORTS_FIELDS = {
    "api_key":       {"required": True, "type": "str", "no_log": True},
    "subdomain":     {"required": True, "type": "str"},
    "title":         {"required": True, "type": "str"},
    "state":         {"required": True, "type": "str", "choices": ["create", "update"]},
    "status":        {"required": True, "type": "str", "choices": ["degraded", "downtime", "maintenance", "resolved"]},
    "report_type":   {"required": True, "type": "str", "choices": ["manual", "maintenance"]},
    "message":       {"required": False, "type": "str"},
    "report_update": {"required": False, "type": "list", "elements": "dict", "options": STATUS_PAGE_REPORT_UPDATES_FIELDS},
    "section_name":  {"required": False, "type": "list", "elements": "str"},
    "published_at":  {"required": False, "type": "str"},
    "starts_at":     {"required": False, "type": "str"},
    "ends_at":       {"required": False, "type": "str"},
}

STATUS_PAGE_REPORTS_REQUIRED_IF = [
    ("state", "create", ("message",)),
    ("state", "update", ("report_update",)),
    ("state", "update", ("starts_at",)),
]


class BetterUptimeStatusPageReportUpdates:
    def __init__(self, module, status_page_id, status_report_id, headers, payload):
        self.module           = module
        self.status_page_id   = status_page_id
        self.status_report_id = status_report_id
        self.headers          = headers
        self.payload          = payload

        self.payload = sanitize_payload(self.payload)
        self.validate_date()

    def validate_date(self):
        """ Validate date format foreach date_fields if set """
        date_fields = ["published_at"]
        for i in date_fields:
            if i in self.payload and not validate_date(self.payload[i], '%Y-%m-%dT%H:%M%z'):
                self.module.fail_json(msg=f"Wrong date format for {i}")

    def create(self):
        """ Create a status page report update"""
        resp = requests.post(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/status-reports/{self.status_report_id}/status-updates", headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.id = resp.json()["data"]["id"]
        else:
            self.module.fail_json(msg=resp.content)


class BetterUptimeStatusPageReport:
    def __init__(self, module):
        self.module  = module

        self.payload       = module.params
        self.status        = self.payload.pop('status')
        self.section_name  = self.payload.pop('section_name')
        self.headers       = {"Authorization": f"Bearer {self.payload.pop('api_key')}"}
        self.state         = self.payload.pop('state')
        self.subdomain     = self.payload.pop('subdomain')
        self.report_update = self.payload.pop('report_update')

        self.status_page_id = None
        self.id = None

        self.payload = sanitize_payload(self.payload)
        self.validate_date()

    def validate_date(self):
        """ Validate date format foreach date_fields if set """
        date_fields = ["published_at", "starts_at", "ends_at"]
        for i in date_fields:
            if i in self.payload and not validate_date(self.payload[i], '%Y-%m-%dT%H:%M%z'):
                self.module.fail_json(msg=f"Wrong date format for {i}")

    def retrieve_status_page_id(self, api_url):
        """ Retrieve the id of a status page if it exists """
        response    = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            if item["attributes"] and item["attributes"]["subdomain"] == self.subdomain:
                self.status_page_id = item["id"]
                return

        if json_object["pagination"]["next"] is not None:
            self.retrieve_status_page_id(json_object["pagination"]["next"])

    def retrieve_status_page_section_ids(self):
        """ Retrieve the ids of status page sections """
        resp = requests.get(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/sections", headers=self.headers)
        retrieved_sections = resp.json()["data"]
        return [int(s["id"]) for s in retrieved_sections if s["attributes"]["name"] in self.section_name]

    def retrieve_status_page_resources_ids(self):
        """ Retrieve the ids of status page resources """
        resp = requests.get(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/resources", headers=self.headers)
        retrieved_resources = resp.json()["data"]
        if self.section_name is None:
            # No section name set => It affects all resources
            self.payload["affected_resources"] = [{"status_page_resource_id": r.get("id"), "status": self.status} for r in retrieved_resources]
        else:
            s = self.retrieve_status_page_section_ids()
            self.payload["affected_resources"] = [{"status_page_resource_id": r.get("id"), "status": self.status} for r in retrieved_resources if r["attributes"]["status_page_section_id"] in s]

    def retrieve_id(self):
        """ Retrieve the id of a status page report if it exists """
        response    = requests.get(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/status-reports", headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            dt_payload = datetime.strptime(self.payload["starts_at"], '%Y-%m-%dT%H:%M%z')
            dt_retrieved = datetime.strptime(item["attributes"]["starts_at"], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)

            if item["attributes"] and \
                    item["attributes"]["title"] == self.payload["title"] and \
                    item["attributes"]["report_type"] == self.payload["report_type"] and \
                    compare_date(dt_payload, dt_retrieved, ["year", "month", "day", "hour", "minute"]):
                self.id = item["id"]
                return

        if json_object["pagination"]["next"] is not None:
            self.retrieve_id(json_object["pagination"]["next"])

    def create(self):
        """ Create a status page report """
        resp = requests.post(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/status-reports", headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.id = resp.json()["data"]["id"]
        else:
            self.module.fail_json(msg=resp.content)

    def manage(self):
        """ Manage a status page report """
        self.retrieve_status_page_id(API_STATUS_PAGES_BASE_URL)
        if self.status_page_id is None:
            self.module.fail_json(msg="Status page not found")

        self.retrieve_status_page_resources_ids()
        if len(self.payload["affected_resources"]) == 0:
            self.module.exit_json(changed=False)

        if self.state == "create":
            self.create()
        elif self.state == "update":
            self.retrieve_id()
            if self.id is None:
                self.module.fail_json(msg="Status page report not found")
            for i in self.report_update:
                i["affected_resources"] = self.payload["affected_resources"]
                b = BetterUptimeStatusPageReportUpdates(self.module, self.status_page_id, self.id, self.headers, i)
                b.create()

        self.module.exit_json(changed=True)


def main():
    module = AnsibleModule(
        argument_spec=STATUS_PAGE_REPORTS_FIELDS,
        supports_check_mode=True,
        required_if=STATUS_PAGE_REPORTS_REQUIRED_IF
    )

    status_page_report_object = BetterUptimeStatusPageReport(module)

    if not module.check_mode:
        status_page_report_object.manage()
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()
