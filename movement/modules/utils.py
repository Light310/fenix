import time

def timing(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        name = func.__name__
        print(f'Timing. {name} : {round(t2 - t1, 4)}')
        
        return res 
    return wrapper

def write_legs_file(data):
    print(f'Writing {data} to the legs file')
    with open('/fenix/tmp/legs_up.txt', 'w') as f:
        f.write(str(data))
