#!/usr/bin/python

import ast
import json
from http import HTTPStatus
from operator import itemgetter

import requests
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.flagsmith import get_project_ids_from_names
from ..module_utils.payload import sanitize_payload

SEGMENT_FIELDS = {
    "api_key":           {"required": True, "type": "str", "no_log": True},
    "base_url":          {"required": True, "type": "str"},
    "state":             {"required": True, "choices": ["present", "absent"], "type": "str"},
    "project_name":      {"required": True, "type": "str"},
    "environment_names": {"required": True, "type": "list"},
    "pricing_plans":     {"required": True, "type": "dict"},
}

class FlagsmithSegmentRulePriorityReorder:
    def __init__(self, module):
        self.module               = module
        self.payload              = module.params
        self.api_key              = self.payload.pop("api_key")
        self.base_url             = self.payload.pop("base_url")
        self.project_name         = self.payload.pop("project_name")
        self.state                = self.payload.pop("state")
        self.environment_names     = self.payload.pop("environment_names")
        self.pricing_plans         = self.payload.pop("pricing_plans")
        self.headers              = {"Authorization": f"Api-Key {self.api_key}", "Accept": "application/json"}
        self.id                   = None
        self.project_id           = None
        self.retrieved_attributes = None
        self.env_api_key          = None
        self.features_env_mapping = {}
        self.segments_config ={}

        self.payload = sanitize_payload(self.payload)
        if 'initial_value' in self.payload:
            # Transform to a valid json string if initial_value is a dict
            try:
                typed_initial_value = ast.literal_eval(self.payload['initial_value'])
                if type(typed_initial_value) is dict:
                    self.payload['initial_value'] = json.dumps(typed_initial_value)
            except ValueError:
                pass

    def retrieve_segment_id(self, segment_name):
        """ Retrieve the id of an segment if it exists """
        response = requests.get(f"{self.base_url}/projects/{self.project_id}/segments/?search={segment_name}", headers=self.headers)
        json_object = response.json()
        for item in json_object["results"]:
            if item["name"] == segment_name:
                return item["id"]
        else:
            self.module.fail_json(msg=f"Segment was not found, {segment_name}")

    def retrieve_environment_id(self, environment_name):
        """ Retrieve the id of an environment if it exists """
        response = requests.get(f"{self.base_url}/projects/{self.project_id}/environments/?search={environment_name}", headers=self.headers)
        json_object = response.json()
        for item in json_object:
            if item["name"] == environment_name:
                return item["id"]
        else:
            self.module.fail_json(msg=f"Environment was not found, {environment_name}")

    def retrieve_associated_features(self,segment_id):
        """ Retrieve the features associated with a segment """
        response = requests.get(f"{self.base_url}/projects/{self.project_id}/segments/{segment_id}/associated-features/", headers=self.headers)
        json_object = response.json()
        if len(json_object["results"]) > 0:
            return json_object["results"]
        else:
            self.module.exit_json(skipped=True, msg=f"no features attached to segment {segment_id}")

    def manage(self):

        # get project id
        project_ids = get_project_ids_from_names(self.base_url, self.headers, [self.project_name])
        if len(project_ids) == 0:
            self.module.fail_json(msg=f"Project was not found, {project_ids}")
        else:
            self.project_id = project_ids[0]

        # get environments id
        for environment in self.environment_names:
            env_id = self.retrieve_environment_id(environment)
            self.features_env_mapping[env_id] = []
        # get segment and features
        for shaun_plan, segment in self.pricing_plans.items():
            segment_id = self.retrieve_segment_id(segment["flagsmith_plan_name"])
            self.segments_config[segment_id]=segment["priority"]
            # retrieve features associated with segment
            for feature in self.retrieve_associated_features(segment_id):
                if feature['environment'] in self.features_env_mapping:
                    self.features_env_mapping[feature['environment']].append(feature)


        # for each feature / env, get the overrides, then reorder based on pricing plan priority (total number of overrides - priority)
        for environment_id, features in self.features_env_mapping.items():
            for feature in features:
                resp = requests.get(f"{self.base_url}/features/feature-segments/?environment={environment_id}&feature={feature['feature']}", headers=self.headers)
                feature_segments = resp.json()['results']
                matched_plans=[]
                for feature_segment in feature_segments[:]:
                    feature_segment_id = feature_segment['segment']
                    if feature_segment['segment'] in self.segments_config.keys():
                        matched_plans.append({"priority": self.segments_config[feature_segment_id], "id": feature_segment['id'] })
                        feature_segments.remove(feature_segment)
                post_data=[]
                for index, item in enumerate(feature_segments):
                    post_data.append({"id": item['id'], "priority": index})
                post_data_length=len(post_data)
                sorted_matched_plans = sorted(matched_plans, key=itemgetter('priority'))

                for sorted_matched_plans in matched_plans:
                    post_data.append({"id":sorted_matched_plans['id'], "priority": post_data_length+sorted_matched_plans['priority']})
                update_request = requests.post(f"{self.base_url}/features/feature-segments/update-priorities/", json=post_data, headers=self.headers)

                if update_request.status_code == HTTPStatus.OK:
                    self.module.exit_json(changed=True)
                else:
                    self.module.fail_json(msg=f"Priority update failed. {update_request.status_code} {update_request.content} \n  Uri: {update_request.url} \n Sent payload: {post_data}")

        self.module.exit_json(changed=True)

def main():
    module = AnsibleModule(
      argument_spec=SEGMENT_FIELDS,
      supports_check_mode=True,
    )

    segment_rule_priority_reorder_object = FlagsmithSegmentRulePriorityReorder(module)

    if not module.check_mode:
        segment_rule_priority_reorder_object.manage()
    else:
        return module.exit_json(changed=False)


if __name__ == "__main__":
    main()
