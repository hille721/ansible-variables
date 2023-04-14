import contextlib
import io

from ansible import constants as C
from ansible.utils.display import Display

display = Display()


def variable_sources(variable_manager, host, var=None, verbosity=0):
    """get vars with sources

    Returns
        [{"name": NAME, "value": VALUE, "source": SOURCE, "files": FILES}]


    """
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
            {"name": var, "value": hostvars.data.get(var), "source": source, "files": []}
            for var, source in hostvars.sources.items()
        ]

    return [{"name": var, "value": hostvars.data.get(var), "source": hostvars.sources.get(var), "files": []}]


def source_mapping(source):
    """Better wording of sources

    Args:
        source (str): original source str out of `vm.get_vars`
    """

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
        if source.startswith(key):
            return value

    return source
