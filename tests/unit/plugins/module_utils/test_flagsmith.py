import pytest
import mock

from plugins.module_utils.flagsmith import get_project_ids_from_names

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
