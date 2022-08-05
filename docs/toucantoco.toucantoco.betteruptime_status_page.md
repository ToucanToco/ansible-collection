# toucantoco.toucantoco.betteruptime_status_page

### Purpose
Manage BetterUptime status pages

### Parameters
| Parameters                      | Required   | Type   | Choices/Default   | Comments    |
|---------------------------------|------------|--------|-------------------|-------------|
| api_key                         | True       | str    |                   |             |
| state                           | True       | str    | present/absent    |             |
| subdomain                       | True       | str    |                   |             |
| scope                           | True       | str    |                   |             |
| sections                        | False      | list   |                   | See below   |
| company_name                    | False      | str    |                   |             |
| company_url                     | False      | str    |                   |             |
| contact_url                     | False      | str    |                   |             |
| logo_url                        | False      | str    |                   |             |
| timezone                        | False      | str    |                   |             |
| custom_domain                   | False      | str    |                   |             |
| custom_css                      | False      | str    |                   |             |
| google_analytics_id             | False      | str    |                   |             |
| min_incident_length             | False      | int    |                   |             |
| announcement                    | False      | str    |                   |             |
| announcement_embed_visible      | False      | bool   |                   |             |
| announcement_embed_custom_css   | False      | str    |                   |             |
| announcement_embed_link         | False      | str    |                   |             |
| subscribable                    | False      | bool   |                   |             |
| hide_from_search_engines        | False      | bool   |                   |             |
| password_enabled                | False      | bool   |                   |             |
| password                        | False      | str    |                   |             |
| history                         | False      | int    |                   |             |

#### Section
| Parameters | Required | Type | Choices/Default | Comments  |
|------------|----------|------|-----------------|-----------|
| name       | False    | str  |                 |           |
| position   | False    | int  |                 |           |
| resource   | False    | list |                 | See below |

#### Resource
| Parameters    | Required   | Type   | Choices/Default   | Comments    |
|---------------|------------|--------|-------------------|-------------|
| resource_name | True       | str    |                   |             |
| public_name   | True       | str    |                   |             |
| resource_type | False      | str    | Monitor           |             |
| widget_type   | False      | str    |                   |             |
| explanation   | False      | str    |                   |             |
| position      | False      | int    |                   |             |
