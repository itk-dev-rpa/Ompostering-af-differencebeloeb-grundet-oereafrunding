"""This module contains the main process of the robot."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import multi_session

from robot_framework import sap


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    session = multi_session.get_all_sap_sessions()[0]
    sap.open_worklist(session)
    sap.filter_searches(session)
    sap.handle_case_or_skip(session, orchestrator_connection)
