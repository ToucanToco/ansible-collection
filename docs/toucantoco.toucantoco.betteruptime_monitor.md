# toucantoco.toucantoco.betteruptime_monitor

### Purpose
Manage BetterUptime monitors

### Parameters
| Parameters                | Required              | Type             | Choices/Default                                                                  | Comments       |
|---------------------------|-----------------------|------------------|----------------------------------------------------------------------------------|----------------|
| api_key                   | True                  | str              |                                                                                  |                |
| url                       | True                  | str              |                                                                                  |                |
| state                     | True                  | str              | present/absent                                                                   |                |
| monitor_type              | True if state present | str              | expected_status_code/imap/keyword/keyword_absence/ping/pop/smtp/status/tcp/udp   |                |
| metadata                  | False                 | listelements     | dict                                                                             |                |
| expected_status_codes     | False                 | listelements     | int                                                                              |                |
| request_headers           | False                 | listelements     | dict                                                                             |                |
| domain_expiration         | False                 | int              |                                                                                  |                |
| ssl_expiration            | False                 | int              |                                                                                  |                |
| policy_name               | False                 | str              |                                                                                  |                |
| follow_redirects          | False                 | bool             |                                                                                  |                |
| required_keyword          | False                 | str              |                                                                                  |                |
| call                      | False                 | bool             | False                                                                            |                |
| sms                       | False                 | bool             | False                                                                            |                |
| email                     | False                 | bool             | True                                                                             |                |
| push                      | False                 | bool             | False                                                                            |                |
| team_wait                 | False                 | int              |                                                                                  |                |
| paused                    | False                 | bool             | False                                                                            |                |
| port                      | False                 | str              |                                                                                  |                |
| regions                   | False                 | listelements     | str                                                                              |                |
| monitor_group_id          | False                 | str              |                                                                                  |                |
| pronounceable_name        | False                 | str              |                                                                                  |                |
| recovery_period           | False                 | int              |                                                                                  |                |
| verify_ssl                | False                 | bool             |                                                                                  |                |
| check_frequency           | False                 | int              | 300                                                                              |                |
| confirmation_period       | False                 | int              | 120                                                                              |                |
| http_method               | False                 | str              |                                                                                  |                |
| request_timeout           | False                 | int              |                                                                                  |                |
| request_body              | False                 | str              |                                                                                  |                |
| auth_username             | False                 | str              |                                                                                  |                |
| auth_password             | False                 | str              |                                                                                  |                |
| maintenance_from          | False                 | str              |                                                                                  |                |
| maintenance_to            | False                 | str              |                                                                                  |                |
| maintenance_timezone      | False                 | str              |                                                                                  |                |
| remember_cookies          | False                 | bool             |                                                                                  |                |
| checks_version            | False                 | str              |                                                                                  |                |
| ip_version                | False                 | str              |                                                                                  |                |
