# import sys
# sys.path.append('/usr/local/lib/python3.5/dist-packages')

import cv2
import numpy as np

from nexus.code.DBScan import MyDBSCAN
from collections import Counter


def find_object(in_image):
    img = n_resize(cv2.imread(in_image, 1))
    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # define range of pink color in HSV
    lower_pink = np.array([170, 50, 50])
    upper_pink = np.array([180, 255, 255])
    # Threshold the HSV image to get only pink colors
    mask = cv2.inRange(hsv, lower_pink, upper_pink)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(img, img, mask=mask)

    potential_points = []
    for i in range(res.shape[0]):
        for j in range(res.shape[1]):
            if int(res[i, j][0]) + int(res[i, j][1]) + int(res[i, j][2]) > 0:
                # print(i,j, res[i,j])
                potential_points.append([i, j])

    clusters = clusterize(potential_points)

    counter = Counter(clusters)

    max_value = 0
    max_index = 0
    for item in counter:
        if counter[item] > max_value:
            max_index = item
            max_value = counter[item]

    result_points = []
    result_points_x = []
    result_points_y = []
    for i in range(len(clusters)):
        if clusters[i] == max_index:
            result_points.append(potential_points[i])
            result_points_x.append(potential_points[i][0])
            result_points_y.append(potential_points[i][1])
            # print('Adding point {0}'.format(potential_points[i]))

    amt = len(result_points)
    center = [np.mean(result_points_x), np.mean(result_points_y)]

    return {'size': amt, 'center': center}


def compare_objects(image1, image2):
    print('Started processing {0}...'.format(image1))
    result1 = find_object(image1)
    print('Started processing {0}...'.format(image2))
    result2 = find_object(image2)
    compare_result = [round(result2['size'] * 1.0 / result1['size'], 5),
                      result2['center'][0] - result1['center'][0],
                      result2['center'][1] - result1['center'][1]]

    return compare_result


def clusterize(input_array):
    clusters = MyDBSCAN(input_array, 2, 2)
    return clusters


def n_resize(source):
    return cv2.resize(source, (450, 600))

