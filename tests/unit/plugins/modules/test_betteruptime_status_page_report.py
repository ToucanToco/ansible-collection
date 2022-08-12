import mock
import pytest

from plugins.modules import betteruptime_status_page_report


@pytest.mark.parametrize(
        "api_response, expected",
        [
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"public_name": "Home"}}]}],
                [{"status_page_resource_id": 5, "status": "maintenance"}],
                id="Maintenance all resources"),
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"public_name": "Home"}}, {"id": 6, "attributes": {"public_name": "Status"}}]}],
                [{"status_page_resource_id": 5, "status": "maintenance"}, {"status_page_resource_id": 6, "status": "maintenance"}],
                id="Maintenance all resources (2)"),
        ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_status_page_report.AnsibleModule')
def test_retrieve_status_page_resources_ids_all_sections(mock_module, mock_requests_get, api_response, expected):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    status_page_report_object              = betteruptime_status_page_report.BetterUptimeStatusPageReport(mock_module)
    status_page_report_object.status       = "maintenance"
    status_page_report_object.section_name = None

    status_page_report_object.retrieve_status_page_resources_ids()

    assert status_page_report_object.payload["affected_resources"] == expected


@pytest.mark.parametrize(
        "api_response, retrieved_sections_ids, expected",
        [
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"public_name": "Home", "status_page_section_id": 2}}, {"id": 7, "attributes": {"public_name": "Home", "status_page_section_id": 4}}]}],
                [2],
                [{"status_page_resource_id": 5, "status": "maintenance"}],
                id="Maintenance of one section having one resource"
            ),
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"public_name": "Home", "status_page_section_id": 2}}, {"id": 6, "attributes": {"public_name": "Home2", "status_page_section_id": 2}}]}],
                [2, 3],
                [{"status_page_resource_id": 5, "status": "maintenance"}, {"status_page_resource_id": 6, "status": "maintenance"}],
                id="Maintenance of one section having two resources"
            ),
        ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_status_page_report.AnsibleModule')
def test_retrieve_status_page_resources_ids_specific_sections(mock_module, mock_requests_get, api_response, retrieved_sections_ids, expected):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    status_page_report_object = betteruptime_status_page_report.BetterUptimeStatusPageReport(mock_module)
    status_page_report_object.status = "maintenance"
    status_page_report_object.section_name = "Front"
    status_page_report_object.retrieve_status_page_section_ids = mock.Mock(return_value=retrieved_sections_ids)

    status_page_report_object.retrieve_status_page_resources_ids()

    assert status_page_report_object.payload["affected_resources"] == expected


@pytest.mark.parametrize(
        "api_response, section_name, expected",
        [
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"name": "Front"}}]}],
                ["Front"],
                [5],
                id="Retrieve one section among one"
            ),
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"name": "Front"}}, {"id": 6, "attributes": {"name": "Back"}}]}],
                ["Front"],
                [5],
                id="Retrieve one section among two"
            ),
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"name": "Front"}}, {"id": 6, "attributes": {"name": "Back"}}]}],
                ["Front", "Back"],
                [5, 6],
                id="Retrieve two section among two"
            ),
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"name": "Front"}}, {"id": 6, "attributes": {"name": "Back"}}]}],
                ["Middle"],
                [],
                id="Retrieve unexisting section"
            ),
        ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_status_page_report.AnsibleModule')
def test_retrieve_status_page_section_ids(mock_module, mock_requests_get, api_response, section_name, expected):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    status_page_report_object = betteruptime_status_page_report.BetterUptimeStatusPageReport(mock_module)
    status_page_report_object.section_name = section_name

    s = status_page_report_object.retrieve_status_page_section_ids()

    assert s == expected


@pytest.mark.parametrize(
        "api_response, payload, expected",
        [
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"title": "MEP", "report_type": "manual", "starts_at": "2021-12-17T11:00:00.000Z"}}]}],
                {"title": "MEP", "report_type": "manual", "starts_at": "2021-12-17T13:00+0200"},
                5,
                id="Retrieve one status page report among one"
            ),
            pytest.param(
                [{"data": [
                    {"id": 5, "attributes": {"title": "MEP", "report_type": "manual", "starts_at": "2021-12-17T11:00:00.000Z"}},
                    {"id": 6, "attributes": {"title": "Incident", "report_type": "manual", "starts_at": "2021-12-19T11:00:00.000Z"}}
                ]}],
                {"title": "Incident", "report_type": "manual", "starts_at": "2021-12-19T13:00+0200"},
                6,
                id="Retrieve one status page report among two"
            ),
            pytest.param(
                [{"data": [{"id": 5, "attributes": {"title": "MEP", "report_type": "manual", "starts_at": "2021-12-17T11:00:00.000Z"}}], "pagination": {"next": None}}],
                {"title": "Incident", "report_type": "manual", "starts_at": "2021-12-17T13:00+0200"},
                None,
                id="Retrieve one status page report that does not exist"
            ),
        ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_status_page_report.AnsibleModule')
def test_retrieve_id(mock_module, mock_requests_get, api_response, payload, expected):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    status_page_report_object = betteruptime_status_page_report.BetterUptimeStatusPageReport(mock_module)
    status_page_report_object.payload = payload

    status_page_report_object.retrieve_id()

    assert status_page_report_object.id == expected
