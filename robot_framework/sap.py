
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

def open_worklist(session):
    session.findById("wnd[0]/tbar[0]/okcd").text = "FPCRPO"
    session.findById("wnd[0]").sendVKey(0)
    # Remove the number from "maks. antal træffere" by writing an empty string
    session.findById("wnd[0]/usr/txt%%DYN001-LOW").text = ""
    # Press the search button
    session.findById("wnd[0]/tbar[1]/btn[8]").press()

def filter(session):
    # Press the 'Selekter' button
    session.findById("wnd[0]/tbar[1]/btn[33]").press()
    # Press Oereafrunding
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").setCurrentCell(9,"TEXT")
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").clickCurrentCell()
    


def format_value(session):
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
    row_count = session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").rowCount
    # Open each case in the search result list
    for row in range(row_count):
        session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").setCurrentCell(row,"")
        session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = row
        session.findById("wnd[0]/tbar[1]/btn[46]").press()

        formatted = format_value(session)

        if -10 <= formatted <= -0.1:
            # Log message
            orchestrator_connection.log_info("Omposterer " + str(formatted))
            # Click 'Omposter Hovedbog'
            session.findById("wnd[0]/usr/subSUB1:SAPLFKCRPO:0100/subSUB_FKT:SAPLFKCRPO:0108/tabsTAB_TRANSFER_POSTING/tabpGLTP").select() 
            # Insert the text 'diff'
            session.findById("wnd[0]/usr/subSUB1:SAPLFKCRPO:0100/subSUB_FKT:SAPLFKCRPO:0108/tabsTAB_TRANSFER_POSTING/tabpGLTP/ssubSUB_GL:SAPLFKCRPO:0120/ctxtFKKCRPO3-KUKON").text = "diff"
            # Click 'Omposter'
            session.findById("wnd[0]/usr/subSUB1:SAPLFKCRPO:0100/subSUB_FKT:SAPLFKCRPO:0108/tabsTAB_TRANSFER_POSTING/tabpGLTP/ssubSUB_GL:SAPLFKCRPO:0120/btnBTM_GL_TRANSF").press()
        else: 
            # Log message
            orchestrator_connection.log_info("Omposterer ikke " + str(formatted))
            # Click 'Gå tilbage til listen'
            session.findById("wnd[0]/tbar[0]/btn[3]").press()


