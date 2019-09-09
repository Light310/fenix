from common.BasicConfig import BasicConfig


calibration_dict = [
    [183, 95], [175, 89], [183, 94], [141, 90],
    [178, 95], [177, 90], [187, 95], [138, 94],
    [182, 95], [182, 90], [177, 99], [129, 92],
    [192, 95], [182, 95], [185, 93], [135, 90]
]

MIN_WIDTH = 500
MAX_WIDTH = 2500
MAX_DIFF = 270  # angle 0 to 270


def arr_diff(array1, array2):
    diff = []
    for index in range(len(array1)):
        a = round(array1[index] - array2[index], 2)
        diff.append(a)
        if abs(a) > 10:
            print(a)

    return diff

cfg = BasicConfig()
sequence_file = cfg.sequence_file

with open(sequence_file, 'r') as f:
    contents = f.readlines()

arrays = []
for item in contents:
    item = item.replace('\n', '').replace('[', '').replace(']', '')
    arr = []
    for number in item.split(','):
        arr.append(float(number))
    arrays.append(arr)

#for index in range(len(arrays)-1):
#    b = arr_diff(arrays[index], arrays[index+1])
#    print(b)


def calibrate_servo(i, input_value):
    return round(calibration_dict[i][0] + (input_value * calibration_dict[i][1] * 1.0 / 90), 4)


for j in range(len(arrays)):
    arr = arrays[j]
    for i in range(16):
        calibrated_servo = calibrate_servo(i, arr[i])
        pulse_width = int(MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * calibrated_servo / MAX_DIFF)
        if pulse_width > MAX_WIDTH or pulse_width < MIN_WIDTH:
            print('PW: {0}, servo : {1}. value : {2}. Row : {3}'.format(pulse_width, i, arr[i], j))
