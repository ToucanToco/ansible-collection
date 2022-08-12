# toucantoco.toucantoco.betteruptime_status_page_report

### Purpose
Manage BetterUptime status page reports

### Parameters
| Parameters    | Required             | Type | Choices/Default                              | Comments                                                            |
|---------------|----------------------|------|----------------------------------------------|---------------------------------------------------------------------|
| api_key       | True                 | str  |                                              |                                                                     |
| subdomain     | True                 | str  |                                              |                                                                     |
| title         | True                 | str  |                                              |                                                                     |
| state         | True                 | str  | create / update                              | create a report or add complementary information to an existing one |
| report_type   | True                 | str  | manual / maintenance                         |                                                                     |
| status        | True                 | str  | degraded / downtime / resolved / maintenance |                                                                     |
| message       | True if state create | str  |                                              |                                                                     |
| report_update | True if state update | list |                                              | See below for options                                               |
| section_name  | False                | list |                                              | Restrict affected resources based on section names                  |
| published_at  | True if state create | str  |                                              |                                                                     |
| starts_at     | True if state update | str  |                                              |                                                                     |
| ends_at       | False                | str  |                                              |                                                                     |

#### Report Update
| Parameters   | Required | Type | Choices/Default | Comments |
|--------------|----------|------|-----------------|----------|
| message      | True     | str  |                 |          |
| published_at | False    | str  |                 |          |

### Notes
- datetime fields `published_at` `starts_at` `ends_at` shoud be set in format `2022-08-02T15:00+0200`
- if `report_type` is `maintenance` only `maintenance` `status` should be used
- if `report_type` is `manual` only `degraded` `downtime` `resolved` `status` should be used
- whend `state` is `update`, associated report is retrieved using `title`, `report_type` and `starts_at` parameters
