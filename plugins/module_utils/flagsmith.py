import requests


def get_organisation_ids_from_names(base_url: str, headers: dict, organisation_names: list) -> list:
    """ Return the ids of the matching organisations"""
    response = requests.get(f"{base_url}/organisations/", headers=headers)
    if response.status_code != 200:
        return []
    json_object = response.json()

    ids = [i['id'] for i in json_object['results'] if i['name'] in organisation_names]

    if len(ids) != len(organisation_names) and json_object['next'] is not None:
        ids = ids + get_organisation_ids_from_names(json_object['next'], headers, organisation_names)

    return ids


def get_user_groups_ids_from_names(base_url: str, headers: dict, organisation_id: int, user_group_names: list) -> list:
    """ Return the ids of the matching user_groups"""
    response = requests.get(f"{base_url}/organisations/{organisation_id}/groups/", headers=headers)
    if response.status_code != 200:
        return []
    json_object = response.json()

    ids = [i['id'] for i in json_object['results'] if i['name'] in user_group_names]

    if len(ids) != len(user_group_names) and json_object['next'] is not None:
        ids = ids + get_user_groups_ids_from_names(json_object['next'], headers, organisation_id, user_group_names)

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
