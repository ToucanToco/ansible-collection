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
  - name:
  type: git
  version: master
```

- Install it with `ansible-galaxy collection install -r requirements.yml`
