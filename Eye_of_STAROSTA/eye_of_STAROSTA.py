
'''
req_dict = {
    'week': None or 'now' or 'next',
    'date': None or '25.09.21 etc.',
    'today': None or True
}
'''
req_dict = {
    'week': False,
    'date': False,
    'today': True
}

def get_timetable_by_week(req_data):
    """Get timetable by week from html req_data

    Args:
        req_data (str): Beautifulsoup
    """
    pass

def get_timetable_by_date(req_data):
    """Get timetable by date from html req_data

    Args:
        req_data (str): Beautifulsoup
    """
    pass

def get_timetable_today(req_data):
    pass

def get_timetable_by_next_week(req_data):
    pass