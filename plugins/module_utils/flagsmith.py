import requests

def get_project_ids_from_names(base_url: str, headers: dict, projects_names: list) -> list:
    """ Return the ids of the matching projects"""
    response = requests.get(f"{base_url}/projects/", headers=headers)
    if response.status_code != 200:
        return []
    json_object = response.json()
    return [i['id'] for i in json_object if i['name'] in projects_names]
