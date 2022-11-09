# toucantoco.toucantoco.flagsmith_stats

### Purpose
Retrieve stats on flagsmith features flags usage

### Parameters
| Parameters        | Required   | Type        | Choices/Default   | Comments            |
| ----------------- | ---------- | ----------- | ----------------- | -----------------   |
| api_key           | True       | str         |                   |                     |
| base_url          | True       | str         |                   | Base URL of the API |
| project_name      | True       | str         |                   |                     |

### Return

```yaml
stats:
    description: dict containing all stats for each feature flag
    type: dict
    returned: always
```

#### Example
```
"stats": [
    {
        "created_date": "2022-08-19T11:02:32.536649Z", // Creation date of the flag
        "datetime": "2022-11-09T10:56:13.248449Z", // Date of the acquisition of the stats
        "default_enabled": true,
        "disabled": 2, // Count of env having this flag disable
        "enabled": 2, // Count of env having this flag enable
        "initial_value": null,
        "is_archived": false,
        "name": "show_demo_button" // Name of the flag
    }
]
```
