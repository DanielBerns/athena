import logging
from pathlib import Path
from typing import Dict, Tuple

from components.core import Crontab
from components.helpers import write_text


def update_crontab(
    crontab_txt: Path,
    commands: Dict[str, Tuple[str, str]]
) -> None:
    crontab = Crontab()
    for key, (a_command, timing) in commands.items():
        crontab.add(
            key, 
            a_command, 
            timing
        )
    crontab.update(crontab_txt)
