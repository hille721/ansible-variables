from ansible import constants as C
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

from ansible_variables.utils.vars import variable_sources

C.set_constant("CONFIG_FILE", "tests/test_data/ansible.cfg")

loader = DataLoader()
inventory = InventoryManager(loader=loader, sources=["tests/test_data/inventory"])
variable_manager = VariableManager(loader=loader, inventory=inventory)


def test_from_all():
    for server in ["server1", "server2", "server3"]:
        sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host(server))
        assert (
            "from_all",
            "hello",
            "group vars, precedence entry 'all_plugins_inventory'",
        ) in [(source.name, source.value, source.source) for source in sources]


def test_server2():
    sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host("server2"), var="test")
    assert [
        (
            "test",
            "from_groupA",
            "group vars, precedence entry 'groups_plugins_inventory'",
        )
    ] == [(source.name, source.value, source.source) for source in sources]


def test_server3():
    sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host("server3"), var="test")
    assert [
        (
            "test",
            "from_groupB",
            "group vars, precedence entry 'groups_plugins_inventory'",
        )
    ] == [(source.name, source.value, source.source) for source in sources]


def test_server4():
    sources = variable_sources(variable_manager=variable_manager, host=inventory.get_host("server4"), var="test")
    assert [("test", "from_all", "group vars, precedence entry 'all_plugins_inventory'")] == [
        (source.name, source.value, source.source) for source in sources
    ]


def test_inventory_server1():
    sources = variable_sources(
        variable_manager=variable_manager, host=inventory.get_host("server1"), var="inventory_test_variable"
    )
    assert [("inventory_test_variable", "from_inventory_server1", "host vars for 'server1'")] == [
        (source.name, source.value, source.source) for source in sources
    ]


def test_inventory_server2():
    sources = variable_sources(
        variable_manager=variable_manager, host=inventory.get_host("server2"), var="inventory_test_variable"
    )
    assert [
        (
            "inventory_test_variable",
            "from_inventory_groupA",
            "group vars, precedence entry 'groups_inventory'",
        )
    ] == [(source.name, source.value, source.source) for source in sources]


def test_inventory_server3():
    sources = variable_sources(
        variable_manager=variable_manager, host=inventory.get_host("server3"), var="inventory_test_variable"
    )
    assert [
        (
            "inventory_test_variable",
            "from_inventory_all",
            "group vars, precedence entry 'all_inventory'",
        )
    ] == [(source.name, source.value, source.source) for source in sources]


def test_undefined_variable():
    sources = variable_sources(
        variable_manager=variable_manager, host=inventory.get_host("server1"), var="undefined_variable_blablabla_1234"
    )
    for variable in sources:
        assert variable.name
        assert not variable.value  # should have None value
        assert not variable.source_mapped  # should have None source
