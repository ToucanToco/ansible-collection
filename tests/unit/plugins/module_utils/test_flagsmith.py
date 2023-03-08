import pytest
import mock

from plugins.module_utils.flagsmith import get_project_ids_from_names, get_tag_ids_from_labels, get_organisation_ids_from_names, get_all_environment_keys


@pytest.mark.parametrize(
        "api_response, expected",
        [
            pytest.param(
                [{"next": None, "results": []}],
                [],
                id="Empty"),
            pytest.param(
                [{"next": None, "results": []}],
                [],
                id="Unexisting organisation"),
            pytest.param(
                [{"next": None, "results": [{"name": "myEnv", "id": 4, "api_key": "myKey"}]}],
                ["myKey"],
                id="Existing environment"),
            pytest.param(
                [{"next": "NotNone", "results": [{"name": "notMyEnv", "id": 45, "api_key": "myKey1"}]}, {"next": None, "results": [{"name": "myEnv", "id": 4, "api_key": "myKey2"}]}],
                ["myKey1", "myKey2"],
                id="Existing environment on page two"),
        ]
)
@mock.patch('requests.get')
def test_get_all_environment_keys(mock_requests_get, api_response, expected):
    response = mock.Mock()
    response.status_code = 200
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    res = get_all_environment_keys("dummy", {})
    assert res == expected

@pytest.mark.parametrize(
        "organization_name, api_response, expected",
        [
            pytest.param(
                [],
                [{"next": None, "results": []}],
                [],
                id="Empty"),
            pytest.param(
                ["myOrg"],
                [{"next": None, "results": []}],
                [],
                id="Unexisting organisation"),
            pytest.param(
                ["myOrg"],
                [{"next": None, "results": [{"name": "myOrg", "id": 4}]}],
                [4],
                id="Existing organisation"),
            pytest.param(
                ["myOrg"],
                [{"next": "NotNone", "results": [{"name": "notMyOrg", "id": 45}]}, {"next": None, "results": [{"name": "myOrg", "id": 4}]}],
                [4],
                id="Existing organisation on page two"),
            pytest.param(
                ["myOrg1", "myOrg2"],
                [{"next": "NotNone", "results": [{"name": "myOrg2", "id": 45}]}, {"next": None, "results": [{"name": "myOrg1", "id": 4}]}],
                [45, 4],
                id="Searched organisations on different pages"),
        ]
)
@mock.patch('requests.get')
def test_get_organization_ids_from_names(mock_requests_get, organization_name, api_response, expected):
    response = mock.Mock()
    response.status_code = 200
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    res = get_organisation_ids_from_names("dummy", {}, organization_name)
    assert res == expected


@pytest.mark.parametrize(
        "user_group_name, api_response, expected",
        [
            pytest.param(
                [],
                [{"next": None, "results": []}],
                [],
                id="Empty"),
            pytest.param(
                ["myUserGroup"],
                [{"next": None, "results": []}],
                [],
                id="Unexisting user group"),
            pytest.param(
                ["myUserGroup"],
                [{"next": None, "results": [{"name": "myUserGroup", "id": 4}]}],
                [4],
                id="Existing user group"),
            pytest.param(
                ["myUserGroup"],
                [{"next": "NotNone", "results": [{"name": "notMyUserGroup", "id": 45}]}, {"next": None, "results": [{"name": "myUserGroup", "id": 4}]}],
                [4],
                id="Existing user group on page two"),
            pytest.param(
                ["myUserGroup1", "myUserGroup2"],
                [{"next": "NotNone", "results": [{"name": "myUserGroup2", "id": 45}]}, {"next": None, "results": [{"name": "myUserGroup1", "id": 4}]}],
                [45, 4],
                id="Searched user groups on different pages"),
        ]
)
@mock.patch('requests.get')
def test_get_user_group_ids_from_names(mock_requests_get, user_group_name, api_response, expected):
    response = mock.Mock()
    response.status_code = 200
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    res = get_organisation_ids_from_names("dummy", {}, user_group_name)
    assert res == expected

@pytest.mark.parametrize(
        "projects_names, api_response, expected",
        [
            pytest.param(
                [],
                [[]],
                [],
                id="Empty"),
            pytest.param(
                ["myproject"],
                [[]],
                [],
                id="Unexisting project"),
            pytest.param(
                ["myproject"],
                [[{"name": "myproject", "id": 4}]],
                [4],
                id="Existing project"),
        ]
)
@mock.patch('requests.get')
def test_get_project_ids_from_names(mock_requests_get, projects_names, api_response, expected):
    response = mock.Mock()
    response.status_code = 200
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    res = get_project_ids_from_names("dummy", {}, projects_names)
    assert res == expected


@pytest.mark.parametrize(
        "tags_labels, api_response, expected",
        [
            pytest.param(
                [],
                [{"next": None, "results": []}],
                [],
                id="Empty"),
            pytest.param(
                ["mytag"],
                [{"next": None, "results": []}],
                [],
                id="Unexisting tag"),
            pytest.param(
                ["mytag"],
                [{"next": None, "results": [{"label": "mytag", "id": 4}]}],
                [4],
                id="Existing tag"),
            pytest.param(
                ["mytag"],
                [{"next": "NotNone", "results": [{"label": "Notmytag", "id": 45}]}, {"next": None, "results": [{"label": "mytag", "id": 4}]}],
                [4],
                id="Existing tag on page two"),
            pytest.param(
                ["tag1", "tag2"],
                [{"next": "NotNone", "results": [{"label": "tag2", "id": 45}]}, {"next": None, "results": [{"label": "tag1", "id": 4}]}],
                [45, 4],
                id="Searched tags on different pages"),
        ]
)
@mock.patch('requests.get')
def test_get_tag_ids_from_labels(mock_requests_get, tags_labels, api_response, expected):
    response = mock.Mock()
    response.status_code = 200
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    res = get_tag_ids_from_labels("dummy", {}, 0, tags_labels)
    assert res == expected
