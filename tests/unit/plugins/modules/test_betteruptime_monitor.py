import mock
import pytest

from plugins.modules import betteruptime_monitor
from ansible.module_utils.common.validation import check_required_if


COMMON_ARGS = {
    "api_key":               "MYAPIKEY",
    "url":                   "myInstance.toucantoco.guru",
    "state":                 "present",
    "monitor_type":          "status",
    "metadata":              [],
    "expected_status_codes": "",
    "request_headers":       {},
    "domain_expiration":     "",
    "ssl_expiration":        "",
    "policy_id":             "",
    "follow_redirects":      "",
    "required_keyword":      "",
    "call":                  False,
    "sms":                   False,
    "email":                 True,
    "push":                  False,
    "team_wait":             "",
    "paused":                False,
    "port":                  "",
    "regions":               [],
    "monitor_group_id":      "",
    "pronounceable_name":    "",
    "recovery_period":       "",
    "verify_ssl":            "",
    "check_frequency":       "",
    "confirmation_period":   "",
    "http_method":           "",
    "request_timeout":       "",
    "request_body":          "",
    "auth_username":         "",
    "auth_password":         "",
    "maintenance_from":      "",
    "maintenance_to":        "",
    "maintenance_timezone":  "",
    "remember_cookies":      "",
}


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
