import mock
import pytest

from plugins.modules import betteruptime_status_page
from ansible.module_utils.common.validation import check_required_if


COMMON_ARGS = {
}

@pytest.mark.parametrize("searched_subdomain, api_response, expected_nb_call_api, expected_status_page_id" , [
        pytest.param(
            "myinstance-toucantoco",
            [{"data": [], "pagination": {"next": None}}],
            1, None,
            id="Status Page not found"),
        pytest.param(
            "myinstance-toucantoco",
            [{"data": [{"id": "1", "attributes": {"subdomain": "myinstance-toucantoco"}}], "pagination": {"next": None}}],
            1, "1",
            id="Status Page found - 1 page"),
        pytest.param(
            "myinstance-toucantoco",
            [
                {"data": [{"id": "1", "attributes": {"subdomain": "notmystance-toucantoco"}}], "pagination": {"next": "https://betteruptime.com/api/v2/status-pages?page=2" }},
                {"data": [{"id": "1", "attributes": {"subdomain": "myinstance-toucantoco"}}], "pagination": {"next": None}}
            ],
            2, "1",
            id="Status Page found - 2 pages"),
        pytest.param(
            "myinstance-toucantoco",
            [
                {"data": [{"id": "1", "attributes": {"subdomain": "notmystance-toucantoco"}}, {"id": "2", "attributes": {"subdomain": "stillnotmyinstance-toucantoco"} }],
                   "pagination": {"next": "https://betteruptime.com/api/v2/status-pages?page=2"}},
                {"data": [{"id": "1", "attributes": {"subdomain": "http://still-not-api-toto.toucantoco.guru"}}], "pagination": {"next": None}}
            ],
            2, None,
            id="Status Page not found - 2 pages"),
    ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_retrieve_id(mock_module, mock_requests_get, searched_subdomain, api_response, expected_nb_call_api, expected_status_page_id):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.payload["subdomain"] = searched_subdomain

    status_page_object.retrieve_id(betteruptime_status_page.API_STATUS_PAGES_BASE_URL)

    assert mock_requests_get.call_count == expected_nb_call_api
    assert status_page_object.id == expected_status_page_id

@pytest.mark.parametrize("sections, api_response, expected_create, expected_delete" , [
        pytest.param(
            [{"name":None, "resources":None}],
            [{"data": []}],
            1, 0,
            id="Create a new section"),
        pytest.param(
            [{"name":None, "resources":None}],
            [{"data": [{"id":1, "attributes":{"name":"Backend", "position":1}}]}],
            0, 0,
            id="Section already existing"),
        pytest.param(
            [],
            [{"data": [{"id":1, "attributes":{"name":"Backend", "position":1}}]}],
            0, 1,
            id="Remove section"),
        pytest.param(
            [],
            [{"data": [{"id":1, "attributes":{"name":"Backend", "position":1}}, {"id":1, "attributes":{"name":"Backend - Other", "position":1}}]}],
            0, 2,
            id="Remove multiple sections"),
        pytest.param(
            [],
            [{"data": [{"id":1, "attributes":{"name":"Frontend", "position":1}}]}],
            0, 0,
            id="Do not delete sections not related to the scope"),
    ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPageSection.delete')
@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPageSection.create')
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_manage_sections(mock_module, mock_betteruptime_page_create, mock_betteruptime_page_delete, mock_requests_get, sections, api_response, expected_create, expected_delete):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.sections = sections
    status_page_object.scope = "backend"

    status_page_object.manage_sections()

    assert mock_betteruptime_page_create.call_count == expected_create
    assert mock_betteruptime_page_delete.call_count == expected_delete

@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.retrieve_id')
@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.create')
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_manage_status_page_create(mock_module, mock_create, mock_retrieve_id):
    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.state = "present"
    status_page_object.sections = None

    status_page_object.manage_status_page()

    assert mock_create.call_count == 1

@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.retrieve_id')
@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.update')
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_manage_status_page_update(mock_module, mock_update, mock_retrieve_id):
    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.state = "present"
    status_page_object.id = "1234"
    status_page_object.sections = None

    status_page_object.manage_status_page()

    assert mock_update.call_count == 1

@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.retrieve_id')
@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.delete')
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_manage_status_page_delete(mock_module, mock_delete, mock_retrieve_id):
    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.state = "absent"
    status_page_object.id = "1234"

    status_page_object.manage_status_page()

    assert mock_delete.call_count == 1
