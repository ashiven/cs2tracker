import os
from subprocess import DEVNULL, call

from cs2tracker.constants import (
    BATCH_FILE,
    OS,
    PROJECT_DIR,
    PYTHON_EXECUTABLE,
    RUNNING_IN_EXE,
    OSType,
)
from cs2tracker.util import get_console

WIN_BACKGROUND_TASK_NAME = "CS2Tracker Daily Calculation"
WIN_BACKGROUND_TASK_SCHEDULE = "DAILY"
WIN_BACKGROUND_TASK_TIME = "12:00"
WIN_BACKGROUND_TASK_CMD = (
    f"powershell -WindowStyle Hidden -Command \"Start-Process '{BATCH_FILE}' -WindowStyle Hidden\""
)

console = get_console()


class BackgroundTask:
    @classmethod
    def identify(cls):
        """
        Search the OS for a daily background task that runs the scraper.

        :return: True if a background task is found, False otherwise.
        """
        if OS == OSType.WINDOWS:
            cmd = ["schtasks", "/query", "/tn", WIN_BACKGROUND_TASK_NAME]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            found = return_code == 0
            return found
        else:
            # TODO: implement finder for cron jobs
            return False

    @classmethod
    def _toggle_batch_file(cls, enabled: bool):
        """
        Create or delete a batch file that runs the scraper.

        :param enabled: If True, the batch file will be created; if False, the batch
            file will be deleted.
        """
        if enabled:
            with open(BATCH_FILE, "w", encoding="utf-8") as batch_file:
                if RUNNING_IN_EXE:
                    # The python executable is set to the executable itself
                    # for executables created with PyInstaller
                    batch_file.write(f"{PYTHON_EXECUTABLE} --only-scrape\n")
                else:
                    batch_file.write(f"cd {PROJECT_DIR}\n")
                    batch_file.write(f"{PYTHON_EXECUTABLE} -m cs2tracker --only-scrape\n")
        else:
            if os.path.exists(BATCH_FILE):
                os.remove(BATCH_FILE)

    @classmethod
    def _toggle_windows(cls, enabled: bool):
        """
        Create or delete a daily background task that runs the scraper on Windows.

        :param enabled: If True, the task will be created; if False, the task will be
            deleted.
        """
        cls._toggle_batch_file(enabled)
        if enabled:
            cmd = [
                "schtasks",
                "/create",
                "/tn",
                WIN_BACKGROUND_TASK_NAME,
                "/tr",
                WIN_BACKGROUND_TASK_CMD,
                "/sc",
                WIN_BACKGROUND_TASK_SCHEDULE,
                "/st",
                WIN_BACKGROUND_TASK_TIME,
            ]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            if return_code == 0:
                console.print("[bold green][+] Background task enabled.")
            else:
                console.error("Failed to enable background task.")
        else:
            cmd = ["schtasks", "/delete", "/tn", WIN_BACKGROUND_TASK_NAME, "/f"]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            if return_code == 0:
                console.print("[bold green][-] Background task disabled.")
            else:
                console.error("Failed to disable background task.")

    @classmethod
    def toggle(cls, enabled: bool):
        """
        Create or delete a daily background task that runs the scraper.

        :param enabled: If True, the task will be created; if False, the task will be
            deleted.
        """
        if OS == OSType.WINDOWS:
            cls._toggle_windows(enabled)
        else:
            # TODO: implement toggle for cron jobs
            pass
