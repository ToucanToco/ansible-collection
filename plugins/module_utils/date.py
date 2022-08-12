from datetime import datetime, timezone

def compare_date(a, b, attribute_list) -> bool:
    """ Compare datetime object based on given attribute_list"""
    """ Example of attribute_list: ["month", "day", "hour"] """
    for att in attribute_list:
        if getattr(a.astimezone(timezone.utc), att) != getattr(b.astimezone(timezone.utc), att):
            return False
    return True

def validate_date(date_text, date_format) -> bool:
    """ Validate date str given a format """
    try:
        datetime.strptime(date_text, date_format)
        return True
    except ValueError:
        return False
