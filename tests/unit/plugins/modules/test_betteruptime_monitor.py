import mock
import pytest

from plugins.modules import betteruptime_monitor
from ansible.module_utils.common.validation import check_required_if

@pytest.mark.parametrize("module_args", [
        pytest.param({"monitor_type": "tcp"}, id="TCP without port"),
        pytest.param({"monitor_type": "udp"}, id="UDP without port"),
        pytest.param({"monitor_type": "udp", "port": 2549}, id="UDP without required_keyword"),
        pytest.param({"monitor_type": "expected_status_code"}, id="expected_status_code without expected_status_code"),
        pytest.param({"monitor_type": "keyword"}, id="keyword without required_keyword"),
        pytest.param({"monitor_type": "keyword_absence"}, id="keyword_absence without required_keyword"),
    ]
)
def test_validate_require_if(module_args):
    with pytest.raises(TypeError):
        check_required_if(betteruptime_monitor.MONITOR_REQUIRED_IF, module_args)

@pytest.mark.parametrize("payload, expected_payload" , [
        pytest.param(
            {"url": "www.myinstance.toucantoco.guru"},
            {"url": "www.myinstance.toucantoco.guru"},
            id="No None fields"),
        pytest.param(
            {"url": "www.myinstance.toucantoco.guru", "email": None},
            {"url": "www.myinstance.toucantoco.guru"},
            id="One None field"),
        pytest.param(
            {"url": "www.myinstance.toucantoco.guru", "email": None, "sms": None},
            {"url": "www.myinstance.toucantoco.guru"},
            id="Two None fields"),
        pytest.param(
            {"url": "www.myinstance.toucantoco.guru", "request_headers": []},
            {"url": "www.myinstance.toucantoco.guru", "request_headers": []},
            id="Empty list"),
        pytest.param(
            {"url": "www.myinstance.toucantoco.guru", "paused": False},
            {"url": "www.myinstance.toucantoco.guru", "paused": False},
            id="False boolean"),
    ]
)
@mock.patch('plugins.modules.betteruptime_monitor.AnsibleModule')
def test_sanitize_payload(mock_module, payload, expected_payload):
    monitor_object = betteruptime_monitor.BetterUptimeMonitor(mock_module)
    monitor_object.payload = payload
    monitor_object.sanitize_payload()

    assert monitor_object.payload == expected_payload

@pytest.mark.parametrize("searched_url, api_response, expected_nb_call_api, expected_monitor_id" , [
        pytest.param(
            "http://api-toto.toucantoco.guru",
            [{"data": [], "pagination": {"next": None}}],
            1, None,
            id="Monitor not found"),
        pytest.param(
            "http://api-toto.toucantoco.guru",
            [{"data": [{"id": "1", "attributes": {"url": "http://api-toto.toucantoco.guru"}}], "pagination": {"next": None}}],
            1, "1",
            id="Monitor found - 1 page"),
        pytest.param(
            "http://api-toto.toucantoco.guru",
            [
                {"data": [{"id": "1", "attributes": {"url": "http://not-api-toto.toucantoco.guru"}}], "pagination": {"next": "https://betteruptime.com/api/v2/monitors?page=2" }},
                {"data": [{"id": "1", "attributes": {"url": "http://api-toto.toucantoco.guru"}}], "pagination": {"next": None}}
            ],
            2, "1",
            id="Monitor found - 2 pages"),
        pytest.param(
            "http://api-toto.toucantoco.guru",
            [
                {"data": [{"id": "1", "attributes": {"url": "http://not-api-toto.toucantoco.guru"}}, {"id": "2", "attributes": {"url": "http://not.toucantoco.guru"} }],
                   "pagination": {"next": "https://betteruptime.com/api/v2/monitors?page=2"}},
                {"data": [{"id": "1", "attributes": {"url": "http://still-not-api-toto.toucantoco.guru"}}], "pagination": {"next": None}}
            ],
            2, None,
            id="Monitor not found - 2 pages"),
    ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_monitor.AnsibleModule')
def test_retrieve_id(mock_module, mock_requests_get, searched_url, api_response, expected_nb_call_api, expected_monitor_id):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    monitor_object = betteruptime_monitor.BetterUptimeMonitor(mock_module)
    monitor_object.payload["url"] = searched_url

    monitor_object.retrieve_id(betteruptime_monitor.API_MONITORS_BASE_URL)

    assert mock_requests_get.call_count == expected_nb_call_api
    assert monitor_object.id == expected_monitor_id

@pytest.mark.parametrize("api_response, initial_payload, expected_payload" , [
        pytest.param(
            [{"data": {"attributes":{"url": "www.myinstance.toucantoco.guru", "paused": True, "ssl_expiration": 14}}}],
            {"url": "www.myinstance.toucantoco.guru", "paused": True},
            {},
            id="No new attributes"),
        pytest.param(
            [{"data": {"attributes":{"url": "www.myinstance.toucantoco.guru"}}}],
            {"url": "www.myinstance.toucantoco.guru", "email": True},
            {"email": True},
            id="One new attribute"),
        pytest.param(
            [{"data": {"attributes":{"url": "www.myinstance.toucantoco.guru", "paused": True}}}],
            {"url": "www.myinstance.toucantoco.guru", "paused": False},
            {"paused": False},
            id="One attribute to update"),
        pytest.param(
            [{"data": {"attributes":{"url": "www.myinstance.toucantoco.guru", "requests_headers": []}}}],
            {"url": "www.myinstance.toucantoco.guru", "requests_headers": [{"name": "User-Agent", "value": "AABBCCDDEEFF"}]},
            {"requests_headers": [{"name": "User-Agent", "value": "AABBCCDDEEFF"}]},
            id="Array"),
    ]
)
@mock.patch('requests.get')
@mock.patch('plugins.modules.betteruptime_monitor.AnsibleModule')
def test_diff_payload(mock_module, mock_requests_get, api_response, initial_payload, expected_payload):
    response = mock.Mock()
    response.json.side_effect = api_response
    mock_requests_get.return_value = response

    monitor_object = betteruptime_monitor.BetterUptimeMonitor(mock_module)
    monitor_object.payload = initial_payload

    monitor_object.diff_payload()

    assert monitor_object.payload == expected_payload


@mock.patch('plugins.modules.betteruptime_monitor.BetterUptimeMonitor.retrieve_id')
@mock.patch('plugins.modules.betteruptime_monitor.BetterUptimeMonitor.create')
@mock.patch('plugins.modules.betteruptime_monitor.AnsibleModule')
def test_manage_monitor_create(mock_module, mock_create, mock_retrieve_id):
    monitor_object = betteruptime_monitor.BetterUptimeMonitor(mock_module)
    monitor_object.state = "present"

    monitor_object.manage_monitor()

    assert mock_create.call_count == 1

@mock.patch('plugins.modules.betteruptime_monitor.BetterUptimeMonitor.retrieve_id')
@mock.patch('plugins.modules.betteruptime_monitor.BetterUptimeMonitor.update')
@mock.patch('plugins.modules.betteruptime_monitor.AnsibleModule')
def test_manage_monitor_update(mock_module, mock_update, mock_retrieve_id):
    monitor_object = betteruptime_monitor.BetterUptimeMonitor(mock_module)
    monitor_object.state = "present"
    monitor_object.id = "1234"

    monitor_object.manage_monitor()

    assert mock_update.call_count == 1

@mock.patch('plugins.modules.betteruptime_monitor.BetterUptimeMonitor.retrieve_id')
@mock.patch('plugins.modules.betteruptime_monitor.BetterUptimeMonitor.delete')
@mock.patch('plugins.modules.betteruptime_monitor.AnsibleModule')
def test_manage_monitor_delete(mock_module, mock_delete, mock_retrieve_id):
    monitor_object = betteruptime_monitor.BetterUptimeMonitor(mock_module)
    monitor_object.state = "absent"
    monitor_object.id = "1234"

    monitor_object.manage_monitor()

    assert mock_delete.call_count == 1
