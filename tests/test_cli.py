import pytest

from ansible import constants as C

from ansible_variables.cli.variables import VariablesCLI

C.set_constant("CONFIG_FILE", "tests/test_data/ansible.cfg")
C.set_constant("DEFAULT_HOST_LIST", "tests/test_data/inventory")


def test_parse(capsys):
    """Test ansible-variables parse"""

    variables_cli = VariablesCLI(["ansible-variables"])
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        variables_cli.parse()
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
        captured = capsys.readouterr()
        assert "from_all: hello - inventory group_vars/all" == captured.out.strip()
