from langchain.tools import tool
from datetime import datetime
from app.FirebaseOperations import query_firestore_generic_extended

@tool
def firestore_query_tool(
    user: str,
    month: str | None = None,
    isAllData: bool = False
):
    """
    Docstring for firestore_query_tool
    
    :param user: Description
    :type user: str
    :param month: Description
    :type month: str | None
    :param isAllData: Description
    :type isAllData: bool
    """ 
    if month:
        month = f"{datetime.now().year}-{month}"

    return query_firestore_generic_extended(
        user,
        {
            "month": month,
            "isAllData": isAllData,
            "isQueryToAppFinanceRelated": True
        }
    )

@tool
def get_current_date_tool():
    """
    Returns the current date in YYYY-MM-DD format.
    """
    return datetime.now().strftime("%Y-%m-%d")