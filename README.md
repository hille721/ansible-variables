# Ansible variables

## Installation

```bash
pip install ansible-variables
```

## Usage

```bash
$ ansible-variables -h
usage: ansible-variables [-h] [--version] [-v] [-i INVENTORY] [--vault-id VAULT_IDS]
                         [--ask-vault-password | --vault-password-file VAULT_PASSWORD_FILES] [--playbook-dir BASEDIR] [--var VARIABLE]
                         host

positional arguments:
  host                  Ansible hostname for which variable sources should be printed

optional arguments:
  --ask-vault-password, --ask-vault-pass
                        ask for vault password
  --playbook-dir BASEDIR
                        Since this tool does not use playbooks, use this as a substitute playbook directory. This sets the relative path for
                        many features including roles/ group_vars/ etc.
  --var VARIABLE        Only check for specific variable
  --vault-id VAULT_IDS  the vault identity to use
  --vault-password-file VAULT_PASSWORD_FILES, --vault-pass-file VAULT_PASSWORD_FILES
                        vault password file
  --version             show program's version number, config file location, configured module search path, module location, executable
                        location and exit
  -h, --help            show this help message and exit
  -i INVENTORY, --inventory INVENTORY, --inventory-file INVENTORY
                        specify inventory host path or comma separated host list. --inventory-file is deprecated
  -v, --verbose         Causes Ansible to print more debug messages. Adding multiple -v will increase the verbosity, the builtin plugins
                        currently evaluate up to -vvvvvv. A reasonable level to start is -vvv, connection debugging might require -vvvv.

Show variable sources for a host.
```
