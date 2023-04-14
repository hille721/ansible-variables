import contextlib
from dataclasses import dataclass
import io
from typing import Optional, List

from ansible import constants as C
from ansible.inventory.host import Host
from ansible.utils.display import Display
from ansible.vars.manager import VariableManager

display = Display()


@dataclass
class VariableSource:
    """Class for keeping track of an variable source item"""

    name: str
    value: str
    source: str
    files: Optional[List[str]] = None

    @property
    def source_mapped(self) -> str:
        """Better wording of sources"""

        source_map = {
            # host variable in inventory
            "host vars for": "host variable defined in inventory",
            # group variable in inventory
            "group vars, precedence entry 'groups_inventory'": "group variable defined in inventory",
            # group variable all in inventory
            "group vars, precedence entry 'all_inventory'": "group variable definined in inventory (all)",
            # host_vars
            "inventory host_vars for": "host_vars",
            # group_vars
            "group vars, precedence entry 'groups_plugins_inventory'": "group_vars",
            # group_vars all
            "group vars, precedence entry 'all_plugins_inventory'": "group_vars (all)",
        }

        for key, value in source_map.items():
            if self.source.startswith(key):
                return value

        return self.source


def variable_sources(
    variable_manager: VariableManager, host: Host, var: Optional[str] = None, verbosity: int = 0
) -> List[VariableSource]:
    """get vars with sources"""

    C.DEFAULT_DEBUG = True
    # we are catching the debug messages here
    fileio = io.StringIO()
    with contextlib.redirect_stdout(fileio):
        hostvars = variable_manager.get_vars(host=host)
    output = fileio.getvalue()
    # let's print the output again if the verbosity is high enough
    if verbosity >= 3:
        display.debug(output)
    C.DEFAULT_DEBUG = False

    if not var:
        return [
            VariableSource(name=var, value=hostvars.data.get(var), source=source)
            for var, source in hostvars.sources.items()
        ]

    return [VariableSource(name=var, value=hostvars.data.get(var), source=hostvars.sources.get(var))]
