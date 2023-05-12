"""

Generates Components/Default-Commands.md from sources.

To test - import this from a Django-aware shell, then call run_update.

"""


from os.path import abspath, dirname
from os.path import join as pathjoin

from evennia.utils.utils import callables_from_module, mod_import, variable_from_module

__all__ = "run_update"


PAGE = """
# Default Commands

The full set of default Evennia commands currently contains {ncommands} commands in {nfiles} source
files. Our policy for adding default commands is outlined [here](Default-Command-Syntax). The
[Commands](Commands) documentation explains how Commands work as well as how to make new or customize
existing ones.

> Note that this page is auto-generated. Report problems to the [issue tracker](github:issues).

```{{note}}
Some game-states add their own Commands which are not listed here. Examples include editing a text
with [EvEditor](EvEditor), flipping pages in [EvMore](EvMore) or using the
[Batch-Processor](Batch-Processors)'s interactive mode.
```

{alphabetical}

""".strip()


def run_update(no_autodoc=False):

    if no_autodoc:
        return

    cmdsets = (
        ("evennia.commands.default.cmdset_character", "CharacterCmdSet"),
        ("evennia.commands.default.cmdset_account", "AccountCmdSet"),
        ("evennia.commands.default.cmdset_unloggedin", "UnloggedinCmdSet"),
        ("evennia.commands.default.cmdset_session", "SessionCmdSet"),
    )
    cmd_modules = (
        "evennia.commands.default.account",
        "evennia.commands.default.batchprocess",
        "evennia.commands.default.building",
        "evennia.commands.default.comms",
        "evennia.commands.default.general",
        "evennia.commands.default.help",
        "evennia.commands.default.syscommandsyyp",
        "evennia.commands.default.system",
        "evennia.commands.default.unloggedin",
    )

    cmds_per_cmdset = {}
    cmd_to_cmdset_map = {}
    for modname, cmdsetname in cmdsets:
        cmdset = variable_from_module(modname, variable=cmdsetname)()
        cmdset.at_cmdset_creation()
        cmds_per_cmdset[cmdsetname] = cmdset.commands
        for cmd in cmdset.commands:
            cmd_to_cmdset_map[f"{cmd.__module__}.{cmd.__class__.__name__}"] = cmdset

    cmds_per_module = {}
    cmd_to_module_map = {}
    cmds_alphabetically = []
    for modname in cmd_modules:
        module = mod_import(modname)
        cmds_per_module[module] = [
            cmd for cmd in callables_from_module(module).values() if cmd.__name__.startswith("Cmd")
        ]
        for cmd in cmds_per_module[module]:
            cmd_to_module_map[cmd] = module
            cmds_alphabetically.append(cmd)
    cmds_alphabetically = list(sorted(cmds_alphabetically, key=lambda c: c.key))

    cmd_infos = []
    for cmd in cmds_alphabetically:
        aliases = [
            alias[1:] if alias and alias[0] == "@" else alias for alias in sorted(cmd.aliases)
        ]
        aliases = f" [{', '.join(sorted(cmd.aliases))}]" if aliases else ""
        cmdlink = f"[**{cmd.key}**{aliases}](api:{cmd.__module__}#{cmd.__name__})"
        category = f"help-category: _{cmd.help_category.capitalize()}_"
        if not (
            cmdset := cmd_to_cmdset_map.get(
                f"{cmd.__module__}.{cmd.__name__}", None
            )
        ):
            # we skip commands not in the default cmdsets
            continue

        cmodule = cmdset.__module__
        cname = cmdset.__class__.__name__
        cmdsetlink = f"cmdset: [{cname}](api:{cmodule}#{cname}), "
        cmd_infos.append(f"{cmdlink} ({cmdsetlink}{category})")

    txt = PAGE.format(
        ncommands=len(cmd_to_cmdset_map),
        nfiles=len(cmds_per_module),
        alphabetical="\n".join(f"- {info}" for info in cmd_infos),
    )

    outdir = pathjoin(dirname(dirname(abspath(__file__))), "source", "Components")
    fname = pathjoin(outdir, "Default-Commands.md")

    with open(fname, "w") as fil:
        fil.write(txt)

    print("  -- Updated Default Command index.")


if __name__ == "__main__":
    run_update()
