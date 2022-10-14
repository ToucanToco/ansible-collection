# toucantoco.toucantoco.flagsmith_feature

### Purpose
Manage Flagsmith features

### Parameters
| Parameters        | Required   | Type        | Choices/Default   | Comments            |
| ----------------- | ---------- | ----------- | ----------------- | -----------------   |
| api_key           | True       | str         |                   |                     |
| base_url          | True       | str         |                   | Base URL of the API |
| state             | True       | str         | present/absent    |                     |
| project_name      | True       | str         |                   |                     |
| name              | True       | str         |                   |                     |
| type              | False      | str         |                   |                     |
| default_enabled   | False      | bool        |                   |                     |
| initial_value     | False      | str         |                   |                     |
| description       | False      | str         |                   |                     |
| is_archived       | False      | bool        |                   |                     |
| tags              | False      | List of str |                   |                     |
