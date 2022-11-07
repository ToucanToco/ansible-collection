# Ansible Collection - toucantoco.toucantoco

This Ansible collection includes a variety of Ansible content to help automate the management of our infrastructure.

## Included Content

### Modules

| Name                                                     | Description                                        |
| -------------------------------------------------------- | -------------------------------------------------- |
| toucantoco.toucantoco.betteruptime_monitor               | Create & manage betteruptime monitors              |
| toucantoco.toucantoco.betteruptime_monitor_sla           | Retrieve SLA of monitors                           |
| toucantoco.toucantoco.betteruptime_status_page           | Create & manage betteruptime status pages          |
| toucantoco.toucantoco.betteruptime_status_page_report    | Create & manage betteruptime status page reports   |
| toucantoco.toucantoco.flagsmith_feature                  | Create & manage Flagsmith features                 |
| toucantoco.toucantoco.flagsmith_tag                      | Create & manage Flagsmith tags                     |


### Installing this collection

- Include it in a requirements.yml file
```
---
collections:
  - name: https://github.com/ToucanToco/ansible-collection/releases/download/v0.1.0/toucantoco-toucantoco-0.1.0.tar.gz
```

- Install it with `ansible-galaxy collection install -r requirements.yml`

### Dev

- Run the tests
 ```
 make tests
 ```

### Release

- Update the version of `ansible_collection` by running `make set-version NEW_VERSION=0.4.1`
- Commit the changes on `master` with a commit message following the syntax: `v0.4.1`
- The build is automatically triggered by the Jenkins pipeline
