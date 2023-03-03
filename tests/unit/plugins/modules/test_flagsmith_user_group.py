import mock
import pytest
from plugins.modules import flagsmith_feature, flagsmith_user_group

@pytest.mark.parametrize("params, api_response, expected_nb_call_api, expected_feature_id" , [
        pytest.param(
            {"name": "test"},
            [{"next": None, "results": []}],
            1, None,
            id="User Group not found"),
        pytest.param(
            {"name": "test"},
            [{"next": None, "results": [{"name": "notTest", "id": 4, "users": [], "is_default": False},
             {"name": "test", "id": 32, "users": [], "is_default": False}
            ]}],
            1, 32,
            id="User Group found first page"),
        pytest.param(
            {"name": "test"},
             [{"next": 'NotNone', "results": [{"name": "notTest", "id": 4, "users": [], "is_default":False}]},
             {"next": None, "results": [{"name": "test", "id": 32, "users": [], "is_default": False}]}],
            2, 32,
            id="User Group found on page two"),
    ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.flagsmith_user_group.AnsibleModule')
def test_retrieve_id(mock_module, mock_requests_get, params, api_response, expected_nb_call_api, expected_feature_id):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    user_group_object = flagsmith_user_group.FlagsmithUserGroup(mock_module)
    user_group_object.payload = params

    user_group_object.retrieve_id("dummy_url")

    assert mock_requests_get.call_count == expected_nb_call_api
    assert user_group_object.id == expected_feature_id


@pytest.mark.parametrize("retrieved_attributes, initial_payload, expected_payload", [
        pytest.param(
            {"name": "test", "is_default": True, "users": [{"id": 1, "email": "test@test.com"}]},
            {"name": "test", "is_default": True},
            {},
            id="No new attributes"),
        pytest.param(
            {"name": "test", "is_default": True, "users": [{"id": 1, "email": "test@test.com"}]},
            {"name": "test", "is_default": False},
            {"is_default": False},
            id="Change is_default"),
    ]
)
@mock.patch('plugins.modules.flagsmith_user_group.AnsibleModule')
def test_diff_attributes(mock_module, retrieved_attributes, initial_payload, expected_payload):
    user_group_object = flagsmith_user_group.FlagsmithUserGroup(mock_module)
    user_group_object.retrieved_attributes = retrieved_attributes
    user_group_object.payload = initial_payload

    user_group_object.diff_attributes()

    assert user_group_object.payload == expected_payload


@mock.patch('plugins.modules.flagsmith_user_group.get_organisation_ids_from_names')
@mock.patch('plugins.modules.flagsmith_user_group.FlagsmithUserGroup.retrieve_id')
@mock.patch('plugins.modules.flagsmith_user_group.FlagsmithUserGroup.create')
@mock.patch('plugins.modules.flagsmith_user_group.AnsibleModule')
def test_manage_create(mock_module, mock_create, mock_retrieve_id, mock_get_organisation_ids_from_names):
    user_group_object                 = flagsmith_user_group.FlagsmithUserGroup(mock_module)
    user_group_object.state           = "present"
    user_group_object.payload["name"] = "production"

    user_group_object.manage()

    assert mock_create.call_count == 1

@mock.patch('plugins.modules.flagsmith_user_group.get_organisation_ids_from_names')
@mock.patch('plugins.modules.flagsmith_user_group.FlagsmithUserGroup.retrieve_id')
@mock.patch('plugins.modules.flagsmith_user_group.FlagsmithUserGroup.update')
@mock.patch('plugins.modules.flagsmith_user_group.AnsibleModule')
def test_manage_update(mock_module, mock_update, mock_retrieve_id, mock_get_organisation_ids_from_names):
    user_group_object                 = flagsmith_user_group.FlagsmithUserGroup(mock_module)
    user_group_object.state           = "present"
    user_group_object.payload["name"] = "production"
    user_group_object.id              = "1234"

    user_group_object.manage()

    assert mock_update.call_count == 1

@mock.patch('plugins.modules.flagsmith_user_group.get_organisation_ids_from_names')
@mock.patch('plugins.modules.flagsmith_user_group.FlagsmithUserGroup.retrieve_id')
@mock.patch('plugins.modules.flagsmith_user_group.FlagsmithUserGroup.delete')
@mock.patch('plugins.modules.flagsmith_user_group.AnsibleModule')
def test_manage_delete(mock_module, mock_delete, mock_retrieve_id, mock_get_organisation_ids_from_names):
    user_group_object                 = flagsmith_user_group.FlagsmithUserGroup(mock_module)
    user_group_object.state           = "absent"
    user_group_object.payload["name"] = "test"
    user_group_object.id              = "1234"

    user_group_object.manage()

    assert mock_delete.call_count == 1
