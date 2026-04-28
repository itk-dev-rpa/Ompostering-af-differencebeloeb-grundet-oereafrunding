"""This module contains the main process of the robot."""

import os

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import multi_session
import itk_dev_event_log

from robot_framework import sap


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    event_log = orchestrator_connection.get_constant("Event Log")
    itk_dev_event_log.setup_logging(event_log.value)
    session = multi_session.get_all_sap_sessions()[0]
    sap.open_worklist(session)
    sap.filter_searches(session)
    sap.handle_case_or_skip(session, orchestrator_connection)


if __name__ == "__main__":
    conn_string = os.getenv("OpenOrchestratorConnString")
    crypto_key = os.getenv("OpenOrchestratorKey")
    oc = OrchestratorConnection("Ompostering", conn_string, crypto_key, "", "", "")
    process(oc)
