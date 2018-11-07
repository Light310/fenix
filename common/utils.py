from datetime import datetime


def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def dttm_from_str(in_str):
    return datetime.strptime(in_str, '%Y-%m-%d %H:%M:%S.%f')


def string_to_array(input_str):
    input_str = input_str.replace('[','').replace(']','')
    split = input_str.split(',')
    result = []
    for item in split:
        result.append(int(item))
    return result


def array_to_string(input_array, brackets = 0):
    array_str = ','.join(str(float(e)) for e in input_array)
    if brackets == 1:
        array_str = '[{0}]'.format(array_str)
    return array_str
