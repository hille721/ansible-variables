import contextlib
import io
import re
from dataclasses import dataclass
from typing import List, Optional

from ansible import constants as C
from ansible.inventory.host import Host
from ansible.parsing.dataloader import DataLoader
from ansible.utils.display import Display
from ansible.vars.manager import VariableManager, VarsWithSources

display = Display()


def escape_ansi(line):
    """The debug output contains ANSI codings, we need to remove them"""
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


@dataclass
class VariableSource:
    """Class for keeping track of an variable source item"""

    name: str
    value: str
    source: str
    debuglog: Optional[str] = None

    @property
    def source_mapped(self) -> str:
        """Better wording of sources"""

        source_map = {
            # host variable in inventory
            "host vars for": "inventory file or script host vars",
            # group variable in inventory
            "group vars, precedence entry 'groups_inventory'": "inventory file or script group vars",
            # group variable all in inventory
            "group vars, precedence entry 'all_inventory'": "inventory file or script group vars/all",
            # host_vars
            "inventory host_vars for": "inventory host_vars/*",
            # group_vars
            "group vars, precedence entry 'groups_plugins_inventory'": "inventory group_vars/*",
            # group_vars all
            "group vars, precedence entry 'all_plugins_inventory'": "inventory group_vars/all",
        }

        for key, value in source_map.items():
            if self.source and self.source.startswith(key):
                return value

        return self.source

    @property
    def files(self) -> List[str]:
        return self.parse_files_from_debug_log()

    def parse_files_from_debug_log(self) -> List[str]:
        """The debug output from `variable_manager.get_vars()` contains all filenames
        from which the variables were loaded.

        The line looks like this:
            4890 1681462516.00300: Loading data from ansible-variables/tests/test_data/inventory/group_vars/all.yml
        """

        files = []
        if not self.debuglog:
            return files

        for line in self.debuglog.splitlines():
            found = re.search(r"Loading data from ([^\s]*)", escape_ansi(line))
            if found:
                files.extend(found.groups())

        return files

    def file_occurrences(self, loader: DataLoader):
        """Open the files and check if the variables occur in it"""
        occurrences = []

        for ffile in self.files:
            display.vvv("Checking file %s for occurrence of variable %s" % (ffile, self.name))

            # Setting unsafe=True will prevent deepcopy and will help with performance
            # and it's safe because we're not modifying the content
            content = loader.load_from_file(ffile, unsafe=True)
            if content and self.name in content:
                occurrences.append(ffile)

        return occurrences


def variable_sources(
    variable_manager: VariableManager,
    host: Host,
    var: Optional[str] = None,
) -> List[VariableSource]:
    """get vars with sources"""

    default_debug = C.DEFAULT_DEBUG
    C.DEFAULT_DEBUG = True
    # we are catching the debug messages here
    fileio = io.StringIO()
    with contextlib.redirect_stdout(fileio):
        vars_with_sources: VarsWithSources = variable_manager.get_vars(host=host)
    output = fileio.getvalue()
    C.DEFAULT_DEBUG = default_debug
    # let's print the debug message only if ANSIBLE_DEBUG was enabled before
    if C.DEFAULT_DEBUG:
        display.debug(output)

    if not var:
        return [
            VariableSource(name=var, value=value, source=vars_with_sources.get_source(var), debuglog=output)
            for var, value in vars_with_sources.items()
        ]

    return [
        VariableSource(
            name=var, value=vars_with_sources.get(var), source=vars_with_sources.get_source(var), debuglog=output
        )
    ]
