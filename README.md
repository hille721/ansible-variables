[![PyPI version](https://badge.fury.io/py/ansible-variables.svg)](https://badge.fury.io/py/ansible-variables)

# ansible-variables

The Ansible inventory provides a very powerful framework to declare variables in a hierarchical manner.
There a lof of differnt places where a variable can be definied (inventory, host_vars, groups_vars, ...) and Ansible will merge them in a specific order ("variable precedence" - <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence>).

`ansible-variables` will help to keep track of your host context variables:

* inventory file or script group vars
* inventory group_vars/all
* inventory group_vars/*
* inventory file or script host vars
* inventory host_vars/*

Based on one host it will retun a list with all variables, values and variable type.

## Installation

```bash
pip install ansible-variables
```

## Usage

The command line usage is simmilar to the official Ansible CLI tools, especially like ansible-inventory, thus to see all possible commands and options run

```plain
ansible-variables --help
```

### Get all variables for a host

The basic usage is pretty simple, you only need to pass the Ansible hostname to it:

```plain
ansible-variables server1
```

This results in following simple rich formatted output

```plain
inventory_test_variable: from_inventory_all - inventory file or script group vars/all
remote_user: myremoteuser - inventory file or script group vars
from_all: hello - inventory group_vars/all
operating_system: rhel8 - inventory group_vars/*
foo: bar - inventory host_vars/*
```

The vervosity can be increased Ansible like with `-v`, `-vvv`, ...

With `-v` the inventory files where the variable is defined, will be printed. The last file wins.

```plain
inventory_test_variable: from_inventory_all - inventory file or script group vars/all
remote_user: myremoteuser - inventory file or script group vars
/home/hille/gitrepos/ansible-variables/tests/test_data/inventory/group_vars/all
test: from_all - inventory group_vars/all
/home/hille/gitrepos/ansible-variables/tests/test_data/inventory/group_vars/all
foo: bar - inventory host_vars/*
/home/hille/gitrepos/ansible-variables/tests/test_data/inventory/group_vars/webservers.yml
/home/hille/gitrepos/ansible-variables/tests/test_data/inventory/host_vars/mywebserver.yml
operating_system: rhel8 - inventory group_vars/*
/home/hille/gitrepos/ansible-variables/tests/test_data/inventory/group_vars/webservers.yml
```

With `-vvv` it will also print all files which were considered to look for the variable.

### Get one specific variables for a host

If you are only interested in one variable you can specify it with `--var`:

```plain
ansible-variables mywebserver --var foo
```

Same es above, the verbosity can also increase here.

### More customization

With `--help` you will see which furhter arguments are possible, e.g. you can set the path to your inventory with `-i`

```plain
ansible-variables mywebserver -i /path/to/inventory
```

## Implementation

This tool is tightly coupled to the Ansible library (`ansible-core`) and simple reuses what is already there.
The whole structure and implemntation was inspired and oriented by the implementation of [`ansible-inventory`](https://github.com/ansible/ansible/blob/devel/lib/ansible/cli/inventory.py).

To get the source and the inventory files in which Ansible will look for a variable, we are using a [debug flag](https://github.com/ansible/ansible/blob/devel/lib/ansible/vars/manager.py#L187) in Ansible's `get_vars` method.

As as result, the output of `ansible-variables` can be fully trusted as it uses the same methods as Ansible to get the variable precedence.

## Limitations

* as written in the description, this tool shows only host context varialbe and there does not know anything about playbook or role variables or command line options.
