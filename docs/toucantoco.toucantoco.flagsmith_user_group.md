# toucantoco.toucantoco.flagsmith_user_group

### Purpose
Manage Flagsmith user groups

### Parameters
| Parameters        | Required   | Type   | Choices/Default   | Comments                                                                                        |
| --------------    | ---------- | ------ | ----------------- | ---------------------                                                                           |
| api_key           | True       | str    |                   |                                                                                                 |
| base_url          | True       | str    |                   | Base URL of the API                                                                             |
| state             | True       | str    | present/absent    |                                                                                                 |
| organisation_name | True       | str    |                   |                                                                                                 |
| name              | True       | str    |                   |                                                                                                 |
| is_default        | False      | str    |                   |                                                                                                 |
| permissions       | False      | dict   |                   | organisation key refers to organisation permissions / project key refers to project permissions |

#### Organisation Permission
Has to be set in the organisation key of the permissions dict.

| Parameters     | Required   | Type   | Choices/Default   | Comments              |
| -------------- | ---------- | ------ | ----------------- | --------------------- |
| permissions    | False      | list   |                   |                       |

Available organisation permissions:
- CREATE_PROJECT
- MANAGE_USER_GROUPS

#### Project Permission
Has to be set in the projects key of the permissions dict.

| Parameters     | Required   | Type   | Choices/Default   | Comments              |
| -------------- | ---------- | ------ | ----------------- | --------------------- |
| name           | True       | str    |                   | Name of the project   |
| admin          | False      | bool   |                   |                       |
| permissions    | False      | list   |                   |                       |
| environments   | False      | dict   |                   |                       |

Available project permissions:
- VIEW_PROJECT
- CREATE_ENVIRONMENT
- DELETE_FEATURE
- CREATE_FEATURE
- MANAGE_SEGMENTS

#### Environment Permission
Has to be set in the environments key of the environments dict. It will apply to all environments of the project.

| Parameters     | Required   | Type   | Choices/Default   | Comments              |
| -------------- | ---------- | ------ | ----------------- | --------------------- |
| admin          | False      | bool   |                   |                       |
| permissions    | False      | list   |                   |                       |

Available environment permissions:
- VIEW_ENVIRONMENT
- UPDATE_FEATURE_STATE
- MANAGE_IDENTITIES
- CREATE_CHANGE_REQUEST
- APPROVE_CHANGE_REQUEST
- VIEW_IDENTITIES

### Examples

```yaml
toucantoco.toucantoco.flagsmith_user_group:
  api_key:           myApiKey
  base_url:          https://myFlagsmithUrl.com
  state:             present
  organisation_name: myOrganisation
  name:              myUserGroup
  is_default:        false
  permissions:
    organisation:
      permissions:
        - CREATE_PROJECT
    projects:
      - name: myProject
        admin: false
        permissions:
          - VIEW_PROJECT
        environments:
          admin: false
          permissions:
            - VIEW_ENVIRONMENT

```
