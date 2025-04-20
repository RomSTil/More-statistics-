import datetime

def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%d-%B-%Y')
        return True
    except ValueError:
        return False