import argparse

import rich
from ansible import context
from ansible.cli.arguments import option_helpers as opt_help
from ansible.errors import AnsibleOptionsError, AnsibleUndefinedVariable
from ansible.module_utils._text import to_native
from ansible.utils.display import Display

from ansible_variables import __version__
from ansible_variables.cli import CLI
from ansible_variables.utils.vars import variable_sources

display = Display()

# Internal vars same as defined for ansible-inventory
# pylint: disable=line-too-long
# (https://github.com/ansible/ansible/blob/d081ed36169f4f74512d1707909185281a30e29b/lib/ansible/cli/inventory.py#L28-L46
INTERNAL_VARS = frozenset(
    [
        "ansible_diff_mode",
        "ansible_config_file",
        "ansible_facts",
        "ansible_forks",
        "ansible_inventory_sources",
        "ansible_limit",
        "ansible_playbook_python",
        "ansible_run_tags",
        "ansible_skip_tags",
        "ansible_verbosity",
        "ansible_version",
        "inventory_dir",
        "inventory_file",
        "inventory_hostname",
        "inventory_hostname_short",
        "groups",
        "group_names",
        "omit",
        "playbook_dir",
    ]
)


class AnsibleVariablesVersion(argparse.Action):
    """we want to have our ansible-variables package version in the --version output"""

    def __call__(self, parser, namespace, values, option_string=None):
        ansible_version = to_native(opt_help.version(f"ansible-variables {__version__}"))
        print(ansible_version)
        parser.exit()


class VariablesCLI(CLI):
    """used to display from where a variable value is coming from"""

    name = "ansible-variables"

    def __init__(self, args):
        super().__init__(args)
        self.loader = None
        self.inventory = None
        self.vm = None  # pylint: disable=invalid-name

    def init_parser(self, usage="", desc=None, epilog=None):
        super().init_parser(
            usage="usage: %prog [options] [host]",
            epilog="""Show variable sources for a host.
                    Copyright 2023, Christoph Hille, https://github.com/hille721/ansible-variables.""",
        )
        version_help = (
            "show program's version number, config file location, configured module search path,"
            " module location, executable location and exit"
        )

        self.parser.add_argument("--version", action=AnsibleVariablesVersion, nargs=0, help=version_help)

        opt_help.add_inventory_options(self.parser)
        opt_help.add_vault_options(self.parser)
        opt_help.add_basedir_options(self.parser)

        # remove unused default options
        self.parser.add_argument("--list-hosts", help=argparse.SUPPRESS, action=opt_help.UnrecognizedArgument)
        self.parser.add_argument(
            "-l",
            "--limit",
            help=argparse.SUPPRESS,
            action=opt_help.UnrecognizedArgument,
        )

        self.parser.add_argument(
            "host",
            action="store",
            help="Ansible hostname for which variable sources should be printed",
        )

        self.parser.add_argument(
            "--var",
            action="store",
            default=None,
            dest="variable",
            help="Only check for specific variable",
        )

    def post_process_args(self, options):
        options = super().post_process_args(options)

        display.verbosity = options.verbosity
        self.validate_conflicts(options)

        return options

    def run(self):
        super().run()

        # Initialize needed objects
        self.loader, self.inventory, self.vm = self._play_prereqs()
        verbosity = display.verbosity

        host = self.inventory.get_host(context.CLIARGS["host"])
        if not host:
            raise AnsibleOptionsError("You must pass a single valid host to ansible-variables")

        for variable in variable_sources(
            variable_manager=self.vm,
            host=host,
            var=context.CLIARGS["variable"],
        ):
            if variable.name not in INTERNAL_VARS:
                if context.CLIARGS["variable"] and not variable.value:
                    # variable as options passed which is not defined
                    raise AnsibleUndefinedVariable("Variable %s is not defined" % variable.name)
                rich.print(
                    f"[bold]{variable.name}[/bold]: {variable.value} - [italic]{variable.source_mapped}[/italic]"
                )
                if verbosity >= 1:
                    files = variable.file_occurrences(loader=self.loader)
                    for ffile in files:
                        rich.print(ffile)


def main(args=None):
    VariablesCLI.cli_executor(args)


if __name__ == "__main__":
    main()
