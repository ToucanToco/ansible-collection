import mock
import pytest

from plugins.modules import betteruptime_status_page
from ansible.module_utils.common.validation import check_required_if


COMMON_ARGS = {
}

@pytest.mark.parametrize("payload, expected_payload" , [
        pytest.param(
            {"subdomain": "tesst"},
            {"subdomain": "tesst"},
            id="No None fields"),
        pytest.param(
            {"subdomain": "tesst", "logo_url": None},
            {"subdomain": "tesst"},
            id="One None field"),
        ]
)
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_sanitize_payload(mock_module, payload, expected_payload):
    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.payload = payload
    status_page_object.sanitize_payload()
    assert status_page_object.payload == expected_payload

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

@pytest.mark.parametrize("retrieved_attributes, initial_payload, expected_payload" , [
        pytest.param(
            {"subdomain": "tesst", "company_name": "ToucanToco"},
            {"subdomain": "tesst", "company_name": "ToucanToco"},
            {},
            id="No new attributes"),
        pytest.param(
            {"subdomain": "tesst", "company_name": "ToucanToco", "logo_url": None},
            {"subdomain": "tesst", "company_name": "ToucanToco", "logo_url": "http://MySuperLogo.png"},
            {"logo_url": "http://MySuperLogo.png"},
            id="One new attribute"),
        pytest.param(
            {"subdomain": "tesst", "company_name": "ToucanToco"},
            {"subdomain": "tesst", "company_name": "NewCompany"},
            {"company_name": "NewCompany"},
            id="One attribute to update"),
    ]
)
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_diff_attributes(mock_module, retrieved_attributes, initial_payload, expected_payload):
    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.retrieved_attributes = retrieved_attributes
    status_page_object.payload = initial_payload

    status_page_object.diff_attributes()

    assert status_page_object.payload == expected_payload

@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.retrieve_id')
@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.create')
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_manage_status_page_create(mock_module, mock_create, mock_retrieve_id):
    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.state = "present"

    status_page_object.manage_status_page()

    assert mock_create.call_count == 1

@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.retrieve_id')
@mock.patch('plugins.modules.betteruptime_status_page.BetterUptimeStatusPage.update')
@mock.patch('plugins.modules.betteruptime_status_page.AnsibleModule')
def test_manage_status_page_update(mock_module, mock_update, mock_retrieve_id):
    status_page_object = betteruptime_status_page.BetterUptimeStatusPage(mock_module)
    status_page_object.state = "present"
    status_page_object.id = "1234"

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
