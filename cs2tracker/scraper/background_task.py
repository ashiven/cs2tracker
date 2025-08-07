import os
from subprocess import DEVNULL, STDOUT, CalledProcessError, call, check_output, run

from cs2tracker.constants import (
    BATCH_FILE,
    OS,
    PROJECT_DIR,
    PYTHON_EXECUTABLE,
    RUNNING_IN_EXE,
    OSType,
)
from cs2tracker.util.padded_console import get_console

WIN_BACKGROUND_TASK_NAME = "CS2Tracker Daily Calculation"
WIN_BACKGROUND_TASK_SCHEDULE = "DAILY"
WIN_BACKGROUND_TASK_TIME = "12:00"
WIN_BACKGROUND_TASK_CMD = (
    f"powershell -WindowStyle Hidden -Command \"Start-Process '{BATCH_FILE}' -WindowStyle Hidden\""
)

LINUX_BACKGROUND_TASK_SCHEDULE = "0 12 * * *"
LINUX_BACKGROUND_TASK_CMD = (
    f"bash -c 'cd {PROJECT_DIR} && {PYTHON_EXECUTABLE} -m cs2tracker --only-scrape'"
)
LINUX_BACKGROUND_TASK_CMD_EXE = f"bash -c 'cd {PROJECT_DIR} && {PYTHON_EXECUTABLE} --only-scrape'"

if RUNNING_IN_EXE:
    LINUX_CRON_JOB = f"{LINUX_BACKGROUND_TASK_SCHEDULE} {LINUX_BACKGROUND_TASK_CMD_EXE}"
else:
    LINUX_CRON_JOB = f"{LINUX_BACKGROUND_TASK_SCHEDULE} {LINUX_BACKGROUND_TASK_CMD}"


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
        elif OS == OSType.LINUX:
            try:
                existing_jobs = (
                    check_output(["crontab", "-l"], stderr=STDOUT).decode("utf-8").strip()
                )
            except CalledProcessError:
                existing_jobs = ""

            found = LINUX_CRON_JOB in existing_jobs.splitlines()
            return found
        else:
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
                console.info("Background task enabled.")
            else:
                console.error("Failed to enable background task.")
        else:
            cmd = ["schtasks", "/delete", "/tn", WIN_BACKGROUND_TASK_NAME, "/f"]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            if return_code == 0:
                console.info("Background task disabled.")
            else:
                console.error("Failed to disable background task.")

    @classmethod
    def _toggle_linux(cls, enabled: bool):
        """
        Create or delete a daily background task that runs the scraper on Linux.

        :param enabled: If True, the task will be created; if False, the task will be
            deleted.
        """
        try:
            existing_jobs = check_output(["crontab", "-l"], stderr=STDOUT).decode("utf-8").strip()
        except CalledProcessError:
            existing_jobs = ""

        cron_lines = existing_jobs.splitlines()

        if enabled and LINUX_CRON_JOB not in cron_lines:
            updated_jobs = (
                existing_jobs + "\n" + LINUX_CRON_JOB + "\n"
                if existing_jobs
                else LINUX_CRON_JOB + "\n"
            )
            try:
                run(
                    ["crontab", "-"],
                    input=updated_jobs.encode("utf-8"),
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                    check=True,
                )
                console.info("Background task enabled.")
            except CalledProcessError:
                console.error("Failed to enable background task.")

        elif not enabled and LINUX_CRON_JOB in cron_lines:
            updated_jobs = "\n".join(
                line for line in cron_lines if line.strip() != LINUX_CRON_JOB
            ).strip()
            try:
                if updated_jobs:
                    run(
                        ["crontab", "-"],
                        input=(updated_jobs + "\n").encode("utf-8"),
                        stdout=DEVNULL,
                        stderr=DEVNULL,
                        check=True,
                    )
                else:
                    run(["crontab", "-r"], stdout=DEVNULL, stderr=DEVNULL, check=True)
                console.info("Background task disabled.")
            except CalledProcessError:
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
        elif OS == OSType.LINUX:
            cls._toggle_linux(enabled)
        else:
            pass
