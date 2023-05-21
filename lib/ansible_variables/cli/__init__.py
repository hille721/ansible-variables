import errno
import sys
import traceback
from pathlib import Path

from ansible import constants as C
from ansible import context
from ansible.cli import CLI as ACLI
from ansible.errors import AnsibleError, AnsibleOptionsError, AnsibleParserError
from ansible.module_utils._text import to_text
from ansible.utils.display import Display

display = Display()


class CLI(ACLI):
    """
    Patched `ansible.cli.CLI` class with `CLI.cli_executor` classmethod backported for ansible-core 2.11
    and ansible-core 2.12.
    Can be removed as soon as we will drop the support for ansible-core < 2.13.

    (see https://github.com/ansible/ansible/pull/76021)
    """

    @classmethod
    def cli_executor(cls, args=None):  # pylint: disable=too-many-branches,too-many-statements
        # no change for ansible-core >= 2.13
        if hasattr(super(), "cli_executor"):
            return super().cli_executor(args=args)

        # backporting code from https://github.com/ansible/ansible/blob/v2.13.9/lib/ansible/cli/__init__.py#L574
        if args is None:
            args = sys.argv

        try:
            display.debug("starting run")

            ansible_dir = Path("~/.ansible").expanduser()
            try:
                ansible_dir.mkdir(mode=0o700)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    display.warning(
                        "Failed to create the directory '%s': %s"
                        % (ansible_dir, to_text(exc, errors="surrogate_or_replace"))
                    )
            else:
                display.debug("Created the '%s' directory" % ansible_dir)

            try:
                args = [to_text(a, errors="surrogate_or_strict") for a in args]
            except UnicodeError:
                display.error(
                    """Command line args are not in utf-8, unable to continue.
                    Ansible currently only understands utf-8"""
                )
                display.display("The full traceback was:\n\n%s" % to_text(traceback.format_exc()))
                exit_code = 6
            else:
                cli = cls(args)
                exit_code = cli.run()

        except AnsibleOptionsError as exc:
            cli.parser.print_help()
            display.error(to_text(exc), wrap_text=False)
            exit_code = 5
        except AnsibleParserError as exc:
            display.error(to_text(exc), wrap_text=False)
            exit_code = 4
        # TQM takes care of these, but leaving comment to reserve the exit codes
        #    except AnsibleHostUnreachable as exc:
        #        display.error(str(exc))
        #        exit_code = 3
        #    except AnsibleHostFailed as exc:
        #        display.error(str(exc))
        #        exit_code = 2
        except AnsibleError as exc:
            display.error(to_text(exc), wrap_text=False)
            exit_code = 1
        except KeyboardInterrupt:
            display.error("User interrupted execution")
            exit_code = 99
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if C.DEFAULT_DEBUG:
                # Show raw stacktraces in debug mode, It also allow pdb to
                # enter post mortem mode.
                raise
            have_cli_options = bool(context.CLIARGS)
            display.error("Unexpected Exception, this is probably a bug: %s" % to_text(exc), wrap_text=False)
            if not have_cli_options or have_cli_options and context.CLIARGS["verbosity"] > 2:
                log_only = False
                if hasattr(exc, "orig_exc"):
                    display.vvv("\nexception type: %s" % to_text(type(exc.orig_exc)))
                    why = to_text(exc.orig_exc)
                    if to_text(exc) != why:
                        display.vvv("\noriginal msg: %s" % why)
            else:
                display.display("to see the full traceback, use -vvv")
                log_only = True
            display.display("the full traceback was:\n\n%s" % to_text(traceback.format_exc()), log_only=log_only)
            exit_code = 250

        sys.exit(exit_code)
