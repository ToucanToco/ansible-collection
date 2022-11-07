import pytest
import mock

from plugins.module_utils.flagsmith import get_project_ids_from_names, get_tag_ids_from_labels

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
                [{"next": None, "results":[]}],
                [],
                id="Empty"),
            pytest.param(
                ["mytag"],
                [{"next": None, "results":[]}],
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
