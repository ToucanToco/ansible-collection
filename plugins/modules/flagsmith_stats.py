#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.flagsmith import get_project_ids_from_names, get_all_resources


from datetime import datetime, timezone

TAG_FIELDS = {
    "api_key":      {"required": True, "type": "str", "no_log": True},
    "base_url":     {"required": True, "type": "str"},
    "project_name": {"required": True, "type": "str"},
}


class FlagsmithStats:
    def __init__(self, module):
        self.module       = module
        self.api_key      = module.params.get("api_key")
        self.base_url     = module.params.get("base_url")
        self.project_name = module.params.get("project_name")
        self.headers      = {"Authorization": f"Token {self.api_key}", "Accept": "application/json"}
        self.project_id   = None
        self.features     = None
        self.environments = None
        self.stats        = {}

    def init_stats(self):
        for feature in self.features:
            self.stats[feature['id']] = {}
            self.stats[feature['id']]['name'] = feature['name']
            self.stats[feature['id']]['datetime'] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            self.stats[feature['id']]['enabled'] = 0
            self.stats[feature['id']]['disabled'] = 0
            self.stats[feature['id']]['default_enabled'] = feature['default_enabled']
            self.stats[feature['id']]['initial_value'] = feature['initial_value']
            self.stats[feature['id']]['is_archived'] = feature['is_archived']
            self.stats[feature['id']]['created_date'] = feature['created_date']

    def manage(self):
        """ Manage stats retrieval """
        project_ids = get_project_ids_from_names(self.base_url, self.headers, [self.project_name])
        if len(project_ids) == 0:
            self.module.fail_json(msg="Project was not found")
        else:
            self.project_id = project_ids[0]

        self.features = get_all_resources(f'{self.base_url}/projects/{self.project_id}/features/', self.headers)
        self.init_stats()
        self.environments = get_all_resources(f'{self.base_url}/environments/?project={self.project_id}', self.headers)

        for e in self.environments:
            fs = get_all_resources(f'{self.base_url}/environments/{e["api_key"]}/featurestates/', self.headers)
            for f in fs:
                if f['enabled']:
                    self.stats[f['feature']]['enabled'] = self.stats[f['feature']]['enabled'] + 1
                else:
                    self.stats[f['feature']]['disabled'] = self.stats[f['feature']]['disabled'] + 1

        self.stats = [b for (_, b) in self.stats.items()]


def main():
    module = AnsibleModule(
      argument_spec=TAG_FIELDS,
      supports_check_mode=True,
    )

    stat_object = FlagsmithStats(module)

    if not module.check_mode:
        stat_object.manage()

    res = dict(
        changed=False,
        stats=stat_object.stats
    )

    return module.exit_json(**res)


if __name__ == "__main__":
    main()
