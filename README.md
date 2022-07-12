# Ansible Collection - toucantoco.toucantoco

This Ansible collection includes a variety of Ansible content to help automate the management of our infrastructure.

## Included Content

### Modules

Name | Description
--- | ---
toucantoco.toucantoco.betteruptime_monitor | Create & manage betteruptime monitors

### Installing this collection

- Include it in a requirements.yml file
```
---
collections:
  - name: git@github.com:ToucanToco/ansible-collection.git
  type: git
  version: master
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
