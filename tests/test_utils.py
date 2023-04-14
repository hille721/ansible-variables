from ansible import constants as C
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

from ansible_variables.utils.vars import variable_sources

C.set_constant("CONFIG_FILE", "tests/test_data/ansible.cfg")

loader = DataLoader()
inventory = InventoryManager(loader=loader, sources=["tests/test_data/inventory"])
variable_manager = VariableManager(loader=loader, inventory=inventory)


def test_from_all():
    for server in ["server1", "server2", "server3"]:
        sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host(server))
        assert {
            "name": "from_all",
            "value": "hello",
            "source": "group vars, precedence entry 'all_plugins_inventory'",
            "files": [],
        } in sources


def test_server1():
    sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host("server1"), var="test")
    assert [
        {"name": "test", "value": "from_server1", "source": "inventory host_vars for 'server1'", "files": []}
    ] == sources


def test_server2():
    sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host("server2"), var="test")
    assert [
        {
            "name": "test",
            "value": "from_groupA",
            "source": "group vars, precedence entry 'groups_plugins_inventory'",
            "files": [],
        }
    ] == sources


def test_server3():
    sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host("server3"), var="test")
    assert [
        {
            "name": "test",
            "value": "from_groupB",
            "source": "group vars, precedence entry 'groups_plugins_inventory'",
            "files": [],
        }
    ] == sources


def test_server4():
    sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host("server4"), var="test")
    assert [
        {
            "name": "test",
            "value": "from_all",
            "source": "group vars, precedence entry 'all_plugins_inventory'",
            "files": [],
        }
    ] == sources


def test_inventory_server1():
    sources = variable_sources(
        variable_manager=variable_manager, host=inventory.get_host("server1"), var="inventory_test_variable"
    )
    assert [
        {
            "name": "inventory_test_variable",
            "value": "from_inventory_server1",
            "source": "host vars for 'server1'",
            "files": [],
        }
    ] == sources


def test_inventory_server2():
    sources = variable_sources(
        variable_manager=variable_manager, host=inventory.get_host("server2"), var="inventory_test_variable"
    )
    assert [
        {
            "name": "inventory_test_variable",
            "value": "from_inventory_groupA",
            "source": "group vars, precedence entry 'groups_inventory'",
            "files": [],
        }
    ] == sources


def test_inventory_server3():
    sources = variable_sources(
        variable_manager=variable_manager, host=inventory.get_host("server3"), var="inventory_test_variable"
    )
    assert [
        {
            "name": "inventory_test_variable",
            "value": "from_inventory_all",
            "source": "group vars, precedence entry 'all_inventory'",
            "files": [],
        }
    ] == sources
