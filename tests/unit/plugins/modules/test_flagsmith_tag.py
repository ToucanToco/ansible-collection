import mock
import pytest
from plugins.modules import flagsmith_tag

@pytest.mark.parametrize("params, api_response, expected_nb_call_api, expected_tag_id" , [
        pytest.param(
            {"label": "test"},
            [{"next": None, "results": []}],
            1, None,
            id="Tag not found"),
        pytest.param(
            {"label": "test"},
            [{"next": None, "results": [{"label": "notTest", "id": 4, "color": None, "description": None}, {"label": "test", "id": 32, "color": None, "description": None}]}],
            1, 32,
            id="Tag found first page"),
        pytest.param(
            {"label": "test"},
            [{"next": 'NotNone', "results": [{"label": "notTest", "id": 4, "color": None, "description": None}]},
             {"next": None, "results": [{"label": "test", "id": 32, "color": None, "description": None}] }],
            2, 32,
            id="Tag found on page two"),
    ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.flagsmith_tag.AnsibleModule')
def test_retrieve_id(mock_module, mock_requests_get, params, api_response, expected_nb_call_api, expected_tag_id):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    tag_object = flagsmith_tag.FlagsmithTag(mock_module)
    tag_object.payload = params

    tag_object.retrieve_id("dummy_url")

    assert mock_requests_get.call_count == expected_nb_call_api
    assert tag_object.id == expected_tag_id

@pytest.mark.parametrize("retrieved_attributes, initial_payload, expected_payload" , [
        pytest.param(
            {"label": "test", "color": "#DEADBE", "description": None},
            {"label": "test", "color": "#DEADBE", "description": None},
            {},
            id="No new attributes"),
        pytest.param(
            {"label": "test", "color": "#DEADBE", "description": None},
            {"label": "test", "color": "#FFFFFF", "description": None},
            {"color": "#FFFFFF"},
            id="Color update"),
        pytest.param(
            {"label": "test", "color": "#DEADBE", "description": None},
            {"label": "test", "color": "#DEADBE", "description": "Fantastic description"},
            {"description": "Fantastic description"},
            id="Add description"),
    ]
)
@mock.patch('plugins.modules.flagsmith_tag.AnsibleModule')
def test_diff_attributes(mock_module, retrieved_attributes, initial_payload, expected_payload):
    tag_object = flagsmith_tag.FlagsmithTag(mock_module)
    tag_object.retrieved_attributes = retrieved_attributes
    tag_object.payload = initial_payload

    tag_object.diff_attributes()

    assert tag_object.payload == expected_payload


@mock.patch('plugins.modules.flagsmith_tag.get_project_ids_from_names')
@mock.patch('plugins.modules.flagsmith_tag.FlagsmithTag.retrieve_id')
@mock.patch('plugins.modules.flagsmith_tag.FlagsmithTag.create')
@mock.patch('plugins.modules.flagsmith_tag.AnsibleModule')
def test_manage_create(mock_module, mock_create, mock_retrieve_id, mock_get_project_ids_from_names):
    tag_object = flagsmith_tag.FlagsmithTag(mock_module)
    tag_object.state            = "present"
    tag_object.payload["color"] = None
    tag_object.payload["label"] = "production"

    tag_object.manage()

    assert mock_create.call_count == 1

@mock.patch('plugins.modules.flagsmith_tag.get_project_ids_from_names')
@mock.patch('plugins.modules.flagsmith_tag.FlagsmithTag.retrieve_id')
@mock.patch('plugins.modules.flagsmith_tag.FlagsmithTag.update')
@mock.patch('plugins.modules.flagsmith_tag.AnsibleModule')
def test_manage_update(mock_module, mock_update, mock_retrieve_id, mock_get_project_ids_from_names):
    tag_object = flagsmith_tag.FlagsmithTag(mock_module)
    tag_object.state            = "present"
    tag_object.payload["label"] = "production"
    tag_object.id               = "1234"

    tag_object.manage()

    assert mock_update.call_count == 1

@mock.patch('plugins.modules.flagsmith_tag.get_project_ids_from_names')
@mock.patch('plugins.modules.flagsmith_tag.FlagsmithTag.retrieve_id')
@mock.patch('plugins.modules.flagsmith_tag.FlagsmithTag.delete')
@mock.patch('plugins.modules.flagsmith_tag.AnsibleModule')
def test_manage_delete(mock_module, mock_delete, mock_retrieve_id, mock_get_project_ids_from_names):
    tag_object = flagsmith_tag.FlagsmithTag(mock_module)
    tag_object.state            = "absent"
    tag_object.payload["label"] = "production"
    tag_object.id               = "1234"

    tag_object.manage()

    assert mock_delete.call_count == 1
