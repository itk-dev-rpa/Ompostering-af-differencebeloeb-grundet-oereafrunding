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

if __name__ == "__main__": 
    oc = OrchestratorConnection("Ompostering", "mssql+pyodbc://localhost\SQLEXPRESS01/OpenOrchestrator?driver=ODBC+Driver+17+for+SQL+Server", "DgWSzep2C7khhZnAZTOfz38vqHI3uFBEVZ0BfSmEfF0=", "")
    process(oc)
