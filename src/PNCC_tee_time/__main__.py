"""Entry point for running the package with `python -m PNCC_tee_time`."""

from PNCC_tee_time.automation import main
from PNCC_tee_time.settings import setup_logging

setup_logging()
main()
