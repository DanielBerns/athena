from typing import Dict, Callable
from pathlib import Path
import subprocess
import logging

from components.core.text_lines_with_keys import TextLinesWithKeys

# https://www.adminschoice.com/crontab-quick-reference

import pdb

class CrontabException(Exception):
    pass


class Crontab:
    def __init__(self):
        self._text = TextLinesWithKeys()

    @property
    def text(self) -> TextLinesWithKeys:
        return self._text

    def check_command(self, command: str) -> str:
        item = Path(command).expanduser()
        if item.exists():
            return str(item)
        remark = f"{classname(self):s}.check_command: command doesn't exists {str(item):s}"
        logging.debug(remark)
        raise CrontabException(remark)

    def check_minute(self, minute: str) -> str:
        if minute:
            if minute == "*":
                return minute
            try:
                if 0 <= int(minute) < 60:
                    return minute
                else:
                    remark = f"{classname(self):s}.check_minute: invalid minute range: {minute:s}"
                    logging.debug(remark)
                    raise CrontabException(remark)
            except ValueError:
                remark = f"{classname(self):s}.check_minute: invalid minute value: {minute:s}"
                logging.debug(remark)                
                raise CrontabException(remark)
        else:
            remark = f"{classname(self):s}.check_minute: invalid minute length"
            logging.debug(remark)                
            raise CrontabException(remark)

    def check_hour(self, hour: str) -> str:
        if hour:
            if hour == "*":
                return hour
            try:
                if 0 <= int(hour) <= 23:
                    return hour
                else:
                    remark = f"{classname(self):s}.check_hour: invalid hour range: {hour:s}"
                    logging.debug(remark)                                    
                    raise CrontabException(remark)
            except ValueError:
                remark = f"{classname(self):s}.check_hour: invalid hour value: {hour:s}"
                logging.debug(remark)                                                    
                raise CrontabException(remark)
        else:
            remark = f"{classname(self):s}.check_hour: invalid hour length"
            logging.debug(remark)                
            raise CrontabException(remark)


    def check_day_of_month(self, day_of_month: str) -> str:
        if day_of_month:
            if day_of_month == "*":
                return day_of_month
            try:
                if 1 <= int(day_of_month) <= 31:
                    return day_of_month
                else:
                    remark = f"{classname(self):s}.check_day_of_month: invalid day_of_month range: {day_of_month:s}"
                    logging.debug(remark)                                    
                    raise CrontabException(remark)
            except ValueError:
                remark = f"{classname(self):s}.check_day_of_month: invalid day_of_month value: {day_of_month:s}"
                logging.debug(remark)                                                    
                raise CrontabException(remark)
        else:
            remark = f"{classname(self):s}.check_day_of_month: invalid day_of_month length"
            logging.debug(remark)                
            raise CrontabException(remark)


    def check_month(self, month: str) -> str:
        if month:
            if month == "*":
                return month
            try:
                if 1 <= int(month) <= 12:
                    return month
                else:
                    remark = f"{classname(self):s}.check_hour: invalid month range: {month:s}"
                    logging.debug(remark)                                    
                    raise CrontabException(remark)
            except ValueError:
                remark = f"{classname(self):s}.check_hour: invalid month value: {month:s}"
                logging.debug(remark)                                                    
                raise CrontabException(remark)
        else:
            remark = f"{classname(self):s}.check_hour: invalid month length"
            logging.debug(remark)                
            raise CrontabException(remark)


    def check_day_of_week(self, day_of_week: str) -> str:
        if day_of_week:
            if day_of_week == "*":
                return day_of_week
            try:
                if 0 <= int(day_of_week) <= 6:
                    return day_of_week
                else:
                    remark = f"{classname(self):s}.check_hour: invalid day_of_week range: {day_of_week:s}"
                    logging.debug(remark)                                    
                    raise CrontabException(remark)
            except ValueError:
                remark = f"{classname(self):s}.check_hour: invalid day_of_week value: {day_of_week:s}"
                logging.debug(remark)                                                    
                raise CrontabException(remark)
        else:
            remark = f"{classname(self):s}.check_hour: invalid day_of_week length"
            logging.debug(remark)                
            raise CrontabException(remark)

    def add(
        self,
        key: str,
        command: str,
        timing: str
    ) -> None:
        pdb.set_trace()
        parts = timing.split(' ')
        if len(parts) != 5:
            remark = f"Error. Bad timing: {key:s} - {str(command):s} - {timing:s}"
            logging.debug(remark)
            print(remark)
            raise CrontabException(remark)
        minute: str = parts[0]
        hour: str = parts[1]
        day_of_month: str = parts[2]
        month: str = parts[3]
        day_of_week: str = parts[4]
        try:
            _command = self.check_command(command)
            _minute = self.check_minute(minute)
            _hour = self.check_hour(hour)
            _day_of_month = self.check_day_of_month(day_of_month)
            _month = self.check_month(month)
            _day_of_week = self.check_day_of_week(day_of_week)
        except CrontabException as message:
            logging.debug(f"{str(message):s}")
            remark = " ".join(
                    (   "Erroneous parameters:",
                        command,
                        minute,
                        hour,
                        day_of_month,
                        month,
                        day_of_week,
                    )
            )
            logging.debug(remark)
            raise CrontabException(remark)
        else:
            line = " ".join(
                (_minute, _hour, _day_of_month, _month, _day_of_week, _command)
            )
            self.text.add(key, line)

    def remove(self, key: str) -> None:
        self.text.remove(key)

    def content(self):
        return self.text.content()

    def update(self, crontab_txt: Path) -> None:
        with open(crontab_txt, "a") as target:
            target.write(self.text.content() + "\n")
        cp = subprocess.run(["crontab", str(crontab_txt)])
        if cp.returncode:
            logging.info(f"update_crontab returncode {cp.returncode:d}")
