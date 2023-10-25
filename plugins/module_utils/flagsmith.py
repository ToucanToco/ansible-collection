import requests


def get_all_environment_keys(url: str, headers: dict) -> list:
    """ Return the keys of all environments"""
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    json_object = response.json()

    keys = [i['api_key'] for i in json_object['results']]
    if json_object['next'] is not None:
        keys = keys + get_all_environment_keys(json_object['next'], headers)

    return keys


def get_organisation_ids_from_names(url: str, headers: dict, organisation_names: list) -> list:
    """ Return the ids of the matching organisations"""
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    json_object = response.json()

    ids = [i['id'] for i in json_object['results'] if i['name'] in organisation_names]

    if len(ids) != len(organisation_names) and json_object['next'] is not None:
        ids = ids + get_organisation_ids_from_names(json_object['next'], headers, organisation_names)

    return ids


def get_project_ids_from_names(base_url: str, headers: dict, projects_names: list) -> list:
    """ Return the ids of the matching projects"""
    response = requests.get(f"{base_url}/projects/", headers=headers)
    if response.status_code != 200:
        return []
    json_object = response.json()
    return [i['id'] for i in json_object if i['name'] in projects_names]


def get_tag_ids_from_labels(url: str, headers: dict, project_id: int, tags_labels: list) -> list:
    """ Return the ids of the matching tags"""
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    json_object = response.json()
    ids = [i['id'] for i in json_object['results'] if i['label'] in tags_labels]

    if len(ids) != len(tags_labels) and json_object['next'] is not None:
        ids = ids + get_tag_ids_from_labels(json_object['next'], headers, project_id, tags_labels)

    return ids
