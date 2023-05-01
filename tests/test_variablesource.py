import pytest
from ansible import constants as C
from ansible.errors import AnsibleFileNotFound
from ansible.parsing.dataloader import DataLoader

from ansible_variables.utils.vars import VariableSource

DEBUGLOG = """
29355 1681471136.41205:  29355 1681471136.40830: in VariableManager get_vars()
29355 1681471136.40839: Calling all_inventory to load vars for server1
29355 1681471136.40842: Calling groups_inventory to load vars for server1
29355 1681471136.40850: Calling all_plugins_inventory to load vars for server1
29355 1681471136.40863: Loading VarsModule 'host_group_vars' ansible/plugins/vars/host_group_vars.py
29355 1681471136.40878:        processing dir tests/test_data/inventory/group_vars
29355 1681471136.40885: Loading data from /foo/bar
29355 1681471136.40906: Calling all_plugins_play to load vars for server1
29355 1681471136.40917: Loading VarsModule 'host_group_vars' ansible/plugins/vars/host_group_vars.py
29355 1681471136.40929: Calling groups_plugins_inventory to load vars for server1
29355 1681471136.40941: Loading VarsModule 'host_group_vars' ansible/plugins/vars/host_group_vars.py
29355 1681471136.40950:        processing dir tests/test_data/inventory/group_vars
29355 1681471136.40957: Loading data from /foo/bar.yml
29355 1681471136.40972: Calling groups_plugins_play to load vars for server1
29355 1681471136.40981: Loading VarsModule 'host_group_vars' ansible/plugins/vars/host_group_vars.py
29355 1681471136.41001: Loading VarsModule 'host_group_vars' ansible/plugins/vars/host_group_vars.py
29355 1681471136.41010:        processing dir tests/test_data/inventory/host_vars
29355 1681471136.41017: Loading data from /FOO/BAR2
29355 1681471136.41040: Loading VarsModule 'host_group_vars' ansible/plugins/vars/host_group_vars.py
29355 1681471136.41197: done with get_vars()"""

loader = DataLoader()


def test_init_variable_source():
    var_source = VariableSource(
        name="foo",
        value="bar",
        source="host vars for foobar",
        debuglog=DEBUGLOG,
    )

    assert var_source.files == ["/foo/bar", "/foo/bar.yml", "/FOO/BAR2"]
    assert var_source.source_mapped == "inventory file or script host vars"
    with pytest.raises(AnsibleFileNotFound):
        var_source.file_occurrences(loader=loader)


def test_occurrence():
    C.set_constant("CONFIG_FILE", "tests/test_data/ansible.cfg")

    var_source = VariableSource(
        name="from_all",
        value="bar",
        source="foobar",
        debuglog="""\x1b[1;30m  5108 81472141.303: Loading data from tests/test_data/inventory/group_vars/all/all\x1b[0m
        \x1b[1;30m  5108 81472141.30388: Loading data from tests/test_data/inventory/group_vars/groupA.yml\x1b[0m
        """,
    )

    assert var_source.value == "bar"
    assert var_source.source_mapped == "foobar"
    assert var_source.files == [
        "tests/test_data/inventory/group_vars/all/all",
        "tests/test_data/inventory/group_vars/groupA.yml",
    ]
    assert var_source.file_occurrences(loader=loader) == ["tests/test_data/inventory/group_vars/all/all"]


def test_empty_file():
    C.set_constant("CONFIG_FILE", "tests/test_data/ansible.cfg")

    var_source = VariableSource(
        name="from_all",
        value="bar",
        source="foobar",
        debuglog="Loading data from tests/test_data/inventory/group_vars/all/empty",
    )

    assert var_source.files == [
        "tests/test_data/inventory/group_vars/all/empty",
    ]
    assert not var_source.file_occurrences(loader=loader)
