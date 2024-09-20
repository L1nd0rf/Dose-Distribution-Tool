import os

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import csv
from sklearn.metrics import r2_score


# Method returning the value at a specific distance from the center of a gaussian.
def Gauss(x, Const, Center, Size):
    y = Const * np.exp((-(x - Center) ** 2) / (2 * Size ** 2))

    return y


def theoricDoseDistribution(gui):
    # Threshold defining the position after which the measured data are not taken into consideration, meaning that the
    # Threshold defining the position after which the measured data are not taken into consideration, meaning that the
    # values further from the center than the first value under the threshold*data maximum value are not taken into account
    # gaussian fit.
    threshold = 0.05
    raw_data = pd.read_csv(gui.csv_path.get())
    raw_x = raw_data['Dist'].to_numpy()
    raw_y = raw_data['Dose'].to_numpy()
    raw_y_normalized = raw_y * gui.normalized_factor
    max_index = raw_y_normalized.argmax()  # Finding the index of the max value in the dosimetry data.
    max_value = raw_y_normalized[max_index]  # Finding the max dose of the dosimetry data.

    # First index definition depending on the defined threshold. Half parameter is used to find a first guess of the
    # gaussian (used in curvefit method).
    index_start = max_index
    half1 = max_index
    while index_start > 0 and raw_y_normalized[index_start] > max_value * threshold:
        index_start = index_start - 1
        if raw_y_normalized[index_start] > max_value / 2:
            half1 = half1 - 1
    # Last index definition depending on the defined threshold. Half parameter is used to find a first guess of the
    # gaussian (used in curvefit method).
    index_end = max_index
    half2 = max_index
    while index_end < (raw_y_normalized.size - 1) and raw_y_normalized[index_end] > max_value * threshold:
        index_end = index_end + 1
        if raw_y_normalized[index_end] > max_value / 2:
            half2 = half2 - 1

    # Defining the guess value for the curvefit method.
    guess = [max_value, raw_x[max_index], (raw_x[half2] - raw_y_normalized[half1]) / 2.35]

    # Reduce the dosimetry data to take into consideration the threshold defined.
    x_data = np.asarray(raw_x[index_start + 1: index_end])
    y_data = np.asarray(raw_y_normalized[index_start + 1: index_end])

    # Fitting data with theoretical gaussian curve parameters
    param, cova = curve_fit(Gauss, x_data, y_data, p0=guess)
    fit_const = param[0]
    fit_center = param[1]
    fit_size = param[2]

    # Gaussian curve values definition
    fit_y = Gauss(raw_x, fit_const, fit_center, fit_size)

    # Fit score measurement using R² method.
    fit_score = round(100 * r2_score(raw_y_normalized, fit_y), 2)
    param = np.append(param, fit_score)

    # Writing gaussian fit parameters output in a file
    time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    header = ['A', 'Center', 'Size', 'Fit Score']
    filename = 'Gauss_results_' + time_stamp + '.csv'
    try:
        os.makedirs("../../output/")
    except FileExistsError:
        pass
    with open('../../output/' + filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(param)

    # Centering gaussian
    raw_x_centered = raw_x - fit_center

    # Entends theoric data from -3sigme to 3 sigma
    raw_x_step = raw_x[1] - raw_x[0]
    raw_x_centered_extended = raw_x_centered
    raw_x_steps_to_add = int((3*fit_size - min(abs(raw_x_centered_extended[0]),
                                               abs(raw_x_centered_extended[len(raw_x_centered_extended)-1])))
                             / raw_x_step)
    for i in range(raw_x_steps_to_add - 1):
        raw_x_centered_extended = np.insert(raw_x_centered_extended, 0, raw_x_centered_extended[0] - raw_x_step)
        raw_x_centered_extended = np.append(raw_x_centered_extended, raw_x_centered_extended[len(
            raw_x_centered_extended) - 1] + raw_x_step)

    # Gaussian curve values definition
    fit_y = Gauss(raw_x_centered_extended, fit_const, 0, fit_size)
    return param, raw_x_centered, raw_x_centered_extended, raw_y_normalized, fit_y
