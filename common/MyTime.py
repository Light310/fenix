from datetime import datetime


def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

def dttm_from_str(in_str):
    return datetime.strptime(in_str, '%Y-%m-%d %H:%M:%S.%f')