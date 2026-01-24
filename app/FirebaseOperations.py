
from app.DB.FireBaseInit import firebase_db
from fastapi import HTTPException
from app.auth import create_access_token, create_refresh_token
from datetime import datetime

def validate_user(userId: str) -> dict:
    # Check if user exists in Firestore
    user_ref = firebase_db.collection('users').document(userId)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found.")
    # If user exists, return some user data or tokens as needed
    accessToken = create_access_token(userId)
    refreshToken = create_refresh_token(userId)
    return {"access_token": accessToken, "refresh_token": refreshToken}

def get_user_info(userId: str):
    user_ref = firebase_db.collection('users').document(userId)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user_doc.to_dict():
        raise HTTPException(status_code=404, detail="User data is empty.")
    return {k: v for k, v in user_doc.to_dict().items() if k != 'google_id'}
    
def get_transactions(userId: str):
    transactions_ref = firebase_db.collection('users').document(userId).collection('monthly_data')
    transactions = transactions_ref.stream()
    transaction_list = []
    for transaction_doc in transactions:
        transaction_data = transaction_doc.to_dict()
        if 'transactions' in transaction_data:
            transaction_list.extend(transaction_data['transactions'])
    return transaction_list    

def query_firestore_generic_extended(userId: str, query_json: dict):
    """
    Handles Firestore queries when transactions are stored inside
    monthly documents in an array. Also converts timestamp fields
    into readable datetime strings for LLMs.
    """

    collection_ref = (
        firebase_db.collection("users")
        .document(userId)
        .collection("monthly_data")
    )
    month = query_json.get("month")
    isAllData = query_json.get("isAllData", False)
    filters = {}
    limit = query_json.get("limit")

    transactions = []

    # -------------------------
    # Helper: Convert timestamp → ISO date
    # -------------------------
    def convert_timestamp(value):
        """
        Convert millisecond timestamps into 'YYYY-MM-DD HH:MM:SS' strings.
        """
        try:
            if isinstance(value, (int, float)) and value > 10**11:  # likely ms timestamp
                dt = datetime.fromtimestamp(value / 1000)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
        return value

    def convert_item_timestamps(item):
        """
        Convert timestamp-like fields inside a transaction dict.
        """
        new_item = {}
        for k, v in item.items():
            new_item[k] = convert_timestamp(v)
        return new_item

    # -------------------------
    # 1. Fetch Data
    # -------------------------
    if month and not isAllData:
        doc = collection_ref.document(month).get()
        if doc.exists:
            data = doc.to_dict()
            transactions = data.get("transactions", [])
    else:
        docs = collection_ref.stream()
        for d in docs:
            data = d.to_dict()
            items = data.get("transactions", [])
            transactions.extend(items)

    # -------------------------
    # 2. Apply Filters in Python
    # -------------------------
    def check_filter(item, field, condition):
        raw_value = item.get(field)

        # for numeric comparisons convert amount strings → float
        try:
            numeric_value = float(raw_value)
        except:
            numeric_value = raw_value

        if isinstance(condition, dict):
            for op, value in condition.items():
                if op == "eq" and not (raw_value == value):
                    return False
                if op == "gt" and not (numeric_value > value):
                    return False
                if op == "gte" and not (numeric_value >= value):
                    return False
                if op == "lt" and not (numeric_value < value):
                    return False
                if op == "lte" and not (numeric_value <= value):
                    return False
                if op == "in" and not (raw_value in value):
                    return False
        else:
            if raw_value != condition:
                return False
        return True

    filtered = []

    for t in transactions:
        ok = True
        for field, cond in filters.items():
            if not check_filter(t, field, cond):
                ok = False
                break
        if ok:
            filtered.append(t)

    # -------------------------
    # 3. Apply Limit
    # -------------------------
    if limit:
        filtered = filtered[:limit]

    # -------------------------
    # 4. Convert timestamps for LLM readability
    # -------------------------
    readable = [convert_item_timestamps(item) for item in filtered]

    return readable

