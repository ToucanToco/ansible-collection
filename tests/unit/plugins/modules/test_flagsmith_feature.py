import mock
import pytest
from plugins.modules import flagsmith_feature

@pytest.mark.parametrize("params, api_response, expected_nb_call_api, expected_feature_id" , [
        pytest.param(
            {"name": "test"},
            [{"next": None, "results": []}],
            1, None,
            id="Feature not found"),
        pytest.param(
            {"name": "test"},
            [{"next": None, "results": [
                {"name": "notTest", "type": None, "default_enabled": False, "initial_value": None, "is_archived": False, "tags": [], "id": 4, "description": None},
                {"name": "test", "type": None, "default_enabled": False, "initial_value": None, "is_archived": False, "tags": [], "id": 32, "description": None}
            ]}],
            1, 32,
            id="Feature found first page"),
        pytest.param(
            {"name": "test"},
            [{"next": 'NotNone', "results": [{"name": "notTest", "type": None, "default_enabled": False, "initial_value": None, "is_archived": False, "tags": [], "id": 4, "color": None, "description": None}]},
             {"next": None, "results": [{"name": "test", "type": None, "default_enabled": False, "initial_value": None, "is_archived": False, "tags": [], "id": 32, "color": None, "description": None}] }],
            2, 32,
            id="Feature found on page two"),
    ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.flagsmith_feature.AnsibleModule')
def test_retrieve_id(mock_module, mock_requests_get, params, api_response, expected_nb_call_api, expected_feature_id):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    feature_object = flagsmith_feature.FlagsmithFeature(mock_module)
    feature_object.payload = params

    feature_object.retrieve_id("dummy_url")

    assert mock_requests_get.call_count == expected_nb_call_api
    assert feature_object.id == expected_feature_id


@pytest.mark.parametrize("retrieved_attributes, initial_payload, expected_payload" , [
        pytest.param(
            {"name": "test", "description": None, "tags": [1, 2]},
            {"name": "test", "description": None, "tags": [2, 1]},
            {},
            id="No new attributes"),
        pytest.param(
            {"name": "test", "default_enabled": False, "description": None},
            {"name": "test", "default_enabled": True, "description": None},
            {"default_enabled": True},
            id="Change default_enabled"),
        pytest.param(
            {"name": "test", "description": None, "tags": [1]},
            {"name": "test", "description": None, "tags": [1, 2]},
            {"tags": [1, 2]},
            id="Add tag"),
    ]
)
@mock.patch('plugins.modules.flagsmith_feature.AnsibleModule')
def test_diff_attributes(mock_module, retrieved_attributes, initial_payload, expected_payload):
    feature_object = flagsmith_feature.FlagsmithFeature(mock_module)
    feature_object.retrieved_attributes = retrieved_attributes
    feature_object.payload = initial_payload

    feature_object.diff_attributes()

    assert feature_object.payload == expected_payload


@mock.patch('plugins.modules.flagsmith_feature.get_project_ids_from_names')
@mock.patch('plugins.modules.flagsmith_feature.FlagsmithFeature.retrieve_id')
@mock.patch('plugins.modules.flagsmith_feature.FlagsmithFeature.create')
@mock.patch('plugins.modules.flagsmith_feature.AnsibleModule')
def test_manage_create(mock_module, mock_create, mock_retrieve_id, mock_get_project_ids_from_names):
    feature_object = flagsmith_feature.FlagsmithFeature(mock_module)
    feature_object.state            = "present"
    feature_object.payload["name"] = "production"

    feature_object.manage()

    assert mock_create.call_count == 1

@mock.patch('plugins.modules.flagsmith_feature.get_project_ids_from_names')
@mock.patch('plugins.modules.flagsmith_feature.FlagsmithFeature.retrieve_id')
@mock.patch('plugins.modules.flagsmith_feature.FlagsmithFeature.update')
@mock.patch('plugins.modules.flagsmith_feature.AnsibleModule')
def test_manage_update(mock_module, mock_update, mock_retrieve_id, mock_get_project_ids_from_names):
    feature_object = flagsmith_feature.FlagsmithFeature(mock_module)
    feature_object.state            = "present"
    feature_object.payload["name"] = "production"
    feature_object.id               = "1234"

    feature_object.manage()

    assert mock_update.call_count == 1

@mock.patch('plugins.modules.flagsmith_feature.get_project_ids_from_names')
@mock.patch('plugins.modules.flagsmith_feature.FlagsmithFeature.retrieve_id')
@mock.patch('plugins.modules.flagsmith_feature.FlagsmithFeature.delete')
@mock.patch('plugins.modules.flagsmith_feature.AnsibleModule')
def test_manage_delete(mock_module, mock_delete, mock_retrieve_id, mock_get_project_ids_from_names):
    feature_object                 = flagsmith_feature.FlagsmithFeature(mock_module)
    feature_object.state           = "absent"
    feature_object.payload["name"] = "test"
    feature_object.id              = "1234"

    feature_object.manage()

    assert mock_delete.call_count == 1
