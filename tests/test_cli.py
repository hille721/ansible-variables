import pytest
from ansible import constants as C

from ansible_variables.cli.variables import VariablesCLI, main

C.set_constant("CONFIG_FILE", "tests/test_data/ansible.cfg")
C.set_constant("DEFAULT_HOST_LIST", "tests/test_data/inventory")


def test_main(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main(["ansible-variables"])
    assert pytest_wrapped_e.type == SystemExit
    assert "ansible-variables: error: the following arguments are required: host" in capsys.readouterr().err


def test_cli_config(capsys):
    variables_cli = VariablesCLI(["ansible-variables", "--version"])
    with pytest.raises(SystemExit):
        variables_cli.run()
    assert "tests/test_data/ansible.cfg" in capsys.readouterr().out.splitlines()[1]


def test_cli_from_all(capsys):
    for server in ["server1", "server2", "server3"]:
        variables_cli = VariablesCLI(["ansible-variables", server, "--var", "from_all"])
        variables_cli.run()
        captured = "".join(capsys.readouterr().out.splitlines())
        assert "from_all: hello - inventory group_vars/all" == captured


def test_cli_from_all_v(capsys):
    variables_cli = VariablesCLI(["ansible-variables", "server1", "--var", "from_all", "-v"])
    variables_cli.run()
    captured = "".join(capsys.readouterr().out.splitlines())
    assert "from_all: hello - inventory group_vars/all" in captured
    assert "tests/test_data/inventory/group_vars/all/all" in captured


def test_cli_from_all_vvv(capsys):
    variables_cli = VariablesCLI(["ansible-variables", "server1", "--var", "from_all", "-vvv"])
    variables_cli.run()
    captured = "".join(capsys.readouterr().out.splitlines())
    # assert "from_all: hello - inventory group_vars/all" in captured
    assert "tests/test_data/inventory/group_vars/all/all" in captured
    assert "tests/test_data/inventory/group_vars/groupA.yml" in captured
    assert "tests/test_data/inventory/group_vars/all/empty" in captured
