import requests

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


def get_all_resources(url: str, headers: dict) -> list:
    """ Return all resources """
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    json_object = response.json()
    resources = json_object['results']

    if json_object['next'] is not None:
        resources = resources + get_all_resources(json_object['next'])

    return resources
