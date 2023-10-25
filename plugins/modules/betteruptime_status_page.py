#!/usr/bin/python

import requests
import urllib

from ansible.module_utils.basic import AnsibleModule
from http import HTTPStatus

from ..module_utils.payload import sanitize_payload
from ..module_utils.payload import diff_attributes

API_STATUS_PAGES_BASE_URL = "https://betteruptime.com/api/v2/status-pages"
API_MONITORS_BASE_URL     = "https://betteruptime.com/api/v2/monitors"

STATUS_PAGES_RESOURCE_FIELDS = {
    "resource_name": {"required": True, "type": "str"},
    "public_name":   {"required": True, "type": "str"},
    "resource_type": {"required": False, "type": "str", "default": "Monitor"},
    "widget_type":   {"required": False, "type":  "str"},
    "explanation":   {"required": False, "type": "str"},
    "position":      {"required": False, "type": "int"},
}

STATUS_PAGES_SECTION_FIELDS = {
    "name":      {"required": False, "type":  "str"},
    "position":  {"required": False, "type": "int"},
    "resources": {"required": False, "type": "list", "elements": "dict", "options": STATUS_PAGES_RESOURCE_FIELDS},
}

STATUS_PAGES_FIELDS = {
    "api_key":                       {"required": True, "type": "str", "no_log": True},
    "state":                         {"required": True, "type": "str", "choices": ["present", "absent"]},
    "subdomain":                     {"required": True, "type": "str"},
    "scope":                         {"required": True, "type": "str"},
    "id":                            {"required": False, "type": "str"},
    "sections":                      {"required": False, "type": "list", "elements": "dict", "options": STATUS_PAGES_SECTION_FIELDS},
    "company_name":                  {"required": False, "type": "str"},
    "company_url":                   {"required": False, "type": "str"},
    "contact_url":                   {"required": False, "type": "str"},
    "logo_url":                      {"required": False, "type": "str"},
    "timezone":                      {"required": False, "type": "str"},
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


class BetterUptimeStatusPageResource:
    def __init__(self, module, status_page_id, section_id, headers, payload):
        self.module = module

        self.status_page_id                    = status_page_id
        self.headers                           = headers
        self.payload                           = payload
        self.payload["status_page_section_id"] = section_id

        if "resource_name" in payload:
            self.resource_name = self.payload.pop("resource_name")

        self.id                   = None
        self.retrieved_attributes = None

        self.payload = sanitize_payload(self.payload)

    def retrieve_monitor_id(self, api_url):
        """ Retrieve the id of a monitor if it exists """
        response = requests.get(f"{api_url}?url={urllib.parse.quote(self.resource_name)}", headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            if item["attributes"] and item["attributes"]["url"] == self.resource_name:
                self.payload["resource_id"] = int(item["id"])
                return

        if json_object["pagination"]["next"] is not None:
            self.retrieve_monitor_id(json_object["pagination"]["next"])
        else:
            self.module.fail_json(msg="Cannot find monitor")

    def set_id(self, retrieved_resources):
        """ Set the id if found in retrieved resources"""
        for i in retrieved_resources:
            if i["attributes"]["resource_id"] == self.payload["resource_id"]:
                self.id = int(i["id"])
                self.retrieved_attributes = i["attributes"]

    def create(self):
        """ Create resource """
        resp = requests.post(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/resources", headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.id = resp.json()["data"]["id"]
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing resource """
        self.payload = diff_attributes(self.payload, self.retrieved_attributes)
        if self.payload:
            resp = requests.patch(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/resources/{self.id}", headers=self.headers, json=self.payload)
            if resp.status_code == HTTPStatus.OK:
                return True
            else:
                self.module.fail_json(msg=resp.content)
        return False

    def delete(self):
        """ Delete a resource """
        resp = requests.delete(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/resources/{self.id}", headers=self.headers)

        if resp.status_code != HTTPStatus.NO_CONTENT:
            self.module.fail_json(msg=resp.content)


class BetterUptimeStatusPageSection:
    def __init__(self, module, status_page_id, headers, payload):
        self.module         = module
        self.headers        = headers
        self.status_page_id = status_page_id
        self.payload        = payload
        self.id             = None

        # Poping resources from the payload for later resources creation
        if "resources" in self.payload:
            self.resources = self.payload.pop("resources")
        else:
            self.resources = None

        self.payload = sanitize_payload(self.payload)

    def set_id(self, retrieved_sections):
        """ Set the id if found in retrieved sections"""
        for i in retrieved_sections:
            if i["attributes"]["name"] == self.payload["name"]:
                self.id = int(i["id"])

    def create(self):
        """ Create section """
        resp = requests.post(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/sections", headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.id = resp.json()["data"]["id"]
        else:
            self.module.fail_json(msg=resp.content)

    def delete(self):
        """ Delete section """
        resp = requests.delete(f"{API_STATUS_PAGES_BASE_URL}/{self.status_page_id}/sections/{self.id}", headers=self.headers)

        if resp.status_code != HTTPStatus.NO_CONTENT:
            self.module.fail_json(msg=resp.content)


class BetterUptimeStatusPage:
    def __init__(self, module):
        self.module  = module
        self.changed = False

        self.payload  = module.params
        self.state    = self.payload.pop("state")
        self.sections = self.payload.pop("sections")
        self.scope    = self.payload.pop("scope")
        self.headers  = {"Authorization": f"Bearer {self.payload.pop('api_key')}"}

        if "id" in self.payload and self.payload["id"] != "":
            self.id = self.payload.pop("id")
        else:
            self.id = None

        self.retrieved_attributes = None

        self.sectionList  = []
        self.resourceList = []

        self.payload = sanitize_payload(self.payload)

    def retrieve_id(self, api_url):
        """ Retrieve the id of a status page if it exists """
        response    = requests.get(api_url, headers=self.headers)
        json_object = response.json()

        for item in json_object["data"]:
            if item["attributes"] and item["attributes"]["subdomain"] == self.payload["subdomain"]:
                self.id                   = item["id"]
                self.retrieved_attributes = item["attributes"]
                return

        if json_object["pagination"]["next"] is not None:
            self.retrieve_id(json_object["pagination"]["next"])

    def manage_sections(self):
        """ Manage section of the Status Page """
        resp               = requests.get(f"{API_STATUS_PAGES_BASE_URL}/{self.id}/sections", headers=self.headers)
        retrieved_sections = resp.json()["data"]
        retrieved_sections = [s for s in retrieved_sections if s["attributes"]["name"].startswith(self.scope.capitalize())]

        for section_payload in self.sections:
            section_payload["name"] = ' - '.join(filter(None, [self.scope.capitalize(), section_payload.get("name")]))
            section = BetterUptimeStatusPageSection(self.module, self.id, self.headers, section_payload)
            section.set_id(retrieved_sections)

            self.sectionList.append(section)

            if section.id is None:
                section.create()
                self.changed = True

        # Remove section that exists but are not configured
        for section_to_remove in [i for i in retrieved_sections if int(i["id"]) not in [j.id for j in self.sectionList]]:
            section = BetterUptimeStatusPageSection(self.module, self.id, self.headers, section_to_remove)
            section.id = section_to_remove["id"]
            section.delete()
            self.changed = True

    def manage_resources(self):
        """ Manage ressources of the Status Page """
        resp = requests.get(f"{API_STATUS_PAGES_BASE_URL}/{self.id}/resources", headers=self.headers)
        retrieved_resources = resp.json()["data"]
        retrieved_resources = [r for r in retrieved_resources if r["attributes"]["status_page_section_id"] in [s.id for s in self.sectionList]]

        for section in self.sectionList:
            if section.resources is not None:
                for resource_payload in section.resources:
                    resource = BetterUptimeStatusPageResource(self.module, self.id, section.id, self.headers, resource_payload)
                    resource.retrieve_monitor_id(API_MONITORS_BASE_URL)
                    resource.set_id(retrieved_resources)
                    self.resourceList.append(resource)
                    if resource.id is None:
                        resource.create()
                        self.changed = True
                    else:
                        changed = resource.update()
                        self.changed = self.changed or changed

        # Remove resource that exists but are not configured
        for resource_to_remove in [i for i in retrieved_resources if int(i["id"]) not in [j.id for j in self.resourceList]]:
            resource = BetterUptimeStatusPageResource(self.module, self.id, 0, self.headers, resource_to_remove)
            resource.id = resource_to_remove["id"]
            resource.delete()
            self.changed = True

    def create(self):
        """ Create a new status page """
        resp = requests.post(API_STATUS_PAGES_BASE_URL, headers=self.headers, json=self.payload)
        if resp.status_code == HTTPStatus.CREATED:
            self.id = resp.json()["data"]["id"]
            self.changed = True
        else:
            self.module.fail_json(msg=resp.content)

    def update(self):
        """ Update an existing status page """
        self.payload = diff_attributes(self.payload, self.retrieved_attributes)

        if self.payload:
            resp = requests.patch(f"{API_STATUS_PAGES_BASE_URL}/{self.id}", headers=self.headers, json=self.payload)
            if resp.status_code == HTTPStatus.OK:
                self.changed = True
            else:
                self.module.fail_json(msg=resp.content)

    def delete(self):
        """ Delete a status page """
        resp = requests.delete(f"{API_STATUS_PAGES_BASE_URL}/{self.id}", headers=self.headers)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            self.changed = True
        else:
            self.module.fail_json(msg=resp.content)

    def manage_status_page(self):
        """ Manage state of a status page """

        if self.id is None:
            self.retrieve_id(API_STATUS_PAGES_BASE_URL)

        if self.state == "present":
            if not self.id:
                self.create()
            else:
                self.update()

            if self.sections is not None:
                self.manage_sections()
                self.manage_resources()

        elif self.state == "absent":
            if not self.id:
                self.module.exit_json(changed=False, msg="No status page to delete with the specified domain")
            else:
                self.delete()

        self.module.exit_json(changed=self.changed)


def main():
    module = AnsibleModule(
        argument_spec=STATUS_PAGES_FIELDS,
        supports_check_mode=True,
    )

    status_page_object = BetterUptimeStatusPage(module)

    if not module.check_mode:
        status_page_object.manage_status_page()
    else:
        return module.exit_json(changed=False)


if __name__ == "__main__":
    main()
