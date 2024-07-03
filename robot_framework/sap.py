"""This module handles the relevant cases in SAP"""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import gridview_util


def open_worklist(session):
    """
    Opens the worklist in the SAP application.

    This function navigates to the worklist screen by setting the transaction code to 'FPCRPO'
    and pressing the search button after clearing the 'maks. antal træffere' field.

    Parameters:
    session (SapGuiSession): The active SAP GUI session to interact with.
    """
    session.findById("wnd[0]/tbar[0]/okcd").text = "FPCRPO"
    session.findById("wnd[0]").sendVKey(0)
    # Remove the number from "maks. antal træffere" by writing an empty string
    session.findById("wnd[0]/usr/txt%%DYN001-LOW").text = ""
    # Press the search button
    session.findById("wnd[0]/tbar[1]/btn[8]").press()


def filter_searches(session):
    """
    Filters the search results in the SAP application.

    This function filters the search results by clicking the 'Selekter' button
    and selecting the 'Oereafrunding' option.

    Parameters:
    session (SapGuiSession): The active SAP GUI session to interact with.
    """
    # Press the 'Selekter' button
    session.findById("wnd[0]/tbar[1]/btn[33]").press()
    # Press Oereafrunding
    layout_table = session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell")
    row_index = gridview_util.find_row_index_by_value(layout_table, "VARIANT", "/ØREAFRUND")
    layout_table.setCurrentCell(row_index, "TEXT")
    layout_table.clickCurrentCell()


def format_value(session):
    """
    Formats the value of the 'ForretnPartner' field in the SAP application.

    Retrieves and formats the 'ForretnPartner' value by moving any trailing minus sign to the front,
    removing thousands separators, and adjusting decimal notation.

    Parameters:
    session (SapGuiSession): The active SAP GUI session to interact with.

    Returns:
    float: The formatted numerical value of the 'ForretnPartner' field.
    """
    # Find the relevant value, which is in a wrong format
    unformatted = session.findById("wnd[0]/usr/subSUB1:SAPLFKCRPO:0100/subSUB_SALDO:SAPLFKCRPO:0107/txtFKKCRPO1-GPART_SALDO").text

    # Move the minus to the front of the value
    if unformatted.endswith('-'):
        unformatted = '-' + unformatted[:-1]

    # Remove all periods as they are used as thousands separators
    unformatted = unformatted.replace(".", "")

    # Replace all commas with a period for decimal notation
    unformatted = unformatted.replace(",", ".")
    formatted = float(unformatted)
    return formatted


def handle_case_or_skip(session, orchestrator_connection: OrchestratorConnection):
    """
    Processes each case in the SAP application or skips based on certain conditions.

    Iterates through each case in the search result list, formats the value using 'format_value', and
    decides whether to perform an action based on the formatted value. Logs actions using the
    orchestrator connection.

    Parameters:
    session (SapGuiSession): The active SAP GUI session to interact with.
    orchestrator_connection (OrchestratorConnection): Connection to the orchestrator for logging.
    """
    row_count = session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").rowCount

    # Opens each case from the search result list that has the Status 'Fri'
    for row in range(row_count):
        status = session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").getCellValue(row, "STATE_TXT")

        if status == 'Fri':
            session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").setCurrentCell(row, "")
            session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = row
            # Open the case
            session.findById("wnd[0]/tbar[1]/btn[46]").press()

            # Clicks OK on a pop-up with message: "Position Udlignet". Maybe other pop-ups with same button id will also be dismissed.
            popup_ok_button = session.findById("wnd[1]/tbar[0]/btn[0]", False)
            if popup_ok_button:
                popup_ok_button.press()
                continue

            formatted = format_value(session)

            if -10 <= formatted <= -0.01:
                # Log message
                orchestrator_connection.log_info(f"Omposterer {formatted}")
                # Click 'Omposter Hovedbog'
                session.findById("wnd[0]/usr/subSUB1:SAPLFKCRPO:0100/subSUB_FKT:SAPLFKCRPO:0108/tabsTAB_TRANSFER_POSTING/tabpGLTP").select()
                # Insert the text 'diff'
                session.findById("wnd[0]/usr/subSUB1:SAPLFKCRPO:0100/subSUB_FKT:SAPLFKCRPO:0108/tabsTAB_TRANSFER_POSTING/tabpGLTP/ssubSUB_GL:SAPLFKCRPO:0120/ctxtFKKCRPO3-KUKON").text = "diff"
                # Click 'Omposter'
                session.findById("wnd[0]/usr/subSUB1:SAPLFKCRPO:0100/subSUB_FKT:SAPLFKCRPO:0108/tabsTAB_TRANSFER_POSTING/tabpGLTP/ssubSUB_GL:SAPLFKCRPO:0120/btnBTM_GL_TRANSF").press()
                # Check for popup
                popup = session.findById("wnd[1]/tbar[0]/btn[0]", False)
                if popup:
                    if session.findById("wnd[1]/usr/txtMESSTXT1").text.strip() == "Der sker ingen behandling pga. spærre af":
                        popup.press()
                    else:
                        raise RuntimeError("Unknown popup")
            else:
                # Log message
                orchestrator_connection.log_info(f"Omposterer ikke {formatted}")
                # Click 'Gå tilbage til listen'
                session.findById("wnd[0]/tbar[0]/btn[3]").press()
