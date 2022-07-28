

def sanitize_payload(payload: dict) -> dict:
    """ Return a dict without None fields """
    return {k:v for (k,v) in payload.items() if v is not None}

def diff_attributes(payload: dict, compare: dict) -> dict:
    """ Return a dict with all the attributes that are only present in the payload"""
    return {k:v for (k,v) in payload.items() if (k,v) not in compare.items()}
