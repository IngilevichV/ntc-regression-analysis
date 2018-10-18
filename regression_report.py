import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import os
import math

def check_equal(arr):
   return arr[1:] == arr[:-1]

def regression(x_part, y_part, label_x, label_y, well_num, path, interval_num, slice_of_interval):
    x_part, y_part = np.array(x_part), np.array(y_part)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_part, y_part)
    plt.plot(x_part, y_part, 'o', label=label_x, markersize=7, alpha=0.5)
    plt.plot(x_part, intercept + slope * x_part, 'r', label=label_y)
    plt.title('Скважина: ' + str(well_num) + '; r2: %.2f' % r_value ** 2)
    plt.grid()
    plt.savefig(path + str(well_num) + "_interval_" + str(interval_num) +"_" + str(slice_of_interval) + ".png")
    plt.gcf().clear()
    plt.close()

def regression_line(x_part, y_part):
    x_part, y_part = np.array(x_part), np.array(y_part)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_part, y_part)
    return x_part, intercept + slope * x_part

def delete_nan_values(arr1, arr2):
    index_to_delete = []
    for i in range(len(arr1)):
        if math.isnan(arr1[i]):
            if i not in index_to_delete:
                index_to_delete.append(i)
        if math.isnan(arr2[i]):
            if i not in index_to_delete:
                index_to_delete.append(i)
    arr1_without_nan = []
    arr2_without_nan = []
    for i in range(len(arr1)):
        if i not in index_to_delete:
            arr1_without_nan.append(arr1[i])
            arr2_without_nan.append(arr2[i])
    if len(index_to_delete) > 0:
        return arr1_without_nan, arr2_without_nan
    else:
        arr2_without_nan, arr2_without_nan = arr1, arr2
        return arr1_without_nan, arr2_without_nan


def regression_with_window(x, y, dates, window, interval_num, dict_with_intervals):
    r2 = []
    x_best, y_best = [], []
    new_dates = []

    for i in range(len(x) - window):
        x_part = x[i:i + window]
        y_part = y[i:i + window]
        x_part, y_part = delete_nan_values(x_part, y_part)
        if len(x_part) == 0:
            r2.append(np.nan)
            new_dates.append(np.nan)
        else:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_part, y_part)
            # Фильтрация неменяющихся значений (частая ситуация для обводненности)
            if check_equal(x_part) or check_equal(y_part):
                r2.append(0)
            else:
                r2.append(r_value ** 2)
            if r_value ** 2 > 0.85:
                x_best.append(x_part)
                y_best.append(y_part)
            new_dates.append(dates[i])
    dict_with_intervals[interval_num] = {}
    dict_with_intervals[interval_num]["x_best"] = x_best
    dict_with_intervals[interval_num]["y_best"] = y_best

    return new_dates, r2, dict_with_intervals


def regression_with_window_for_each_interval(xs, ys, dates, window, well_num, dates_zkc=None, dates_pgi=None):
    if len(xs) == 0 or len(ys) == 0 or len(dates) == 0:
        raise Exception('Передан пустой массив')
    if len(xs) != len(ys) or len(ys) != len(dates) or len(xs) != len(dates):
        raise Exception('Массивы должны быть одного размера')

    dict_with_intervals = {}
    plt.figure(figsize=(13, 9))
    interval_num = 1
    for x, y, date in zip(xs, ys, dates):
        if len(x) < window:
            print("Длина интервала %d меньше указанного окна. Для данного участки регрессия с окном не рассчитывается." % interval_num)
        else:
            dates_interval, r2_interval, dict_with_intervals = regression_with_window(x, y, date, window, interval_num, dict_with_intervals)
            plt.plot(dates_interval, r2_interval)
        interval_num += 1

    if dates_zkc and len(dates_zkc) > 0:
        label_zkc = 0
        for date_zkc in dates_zkc:
            if date_zkc <= dates[-1] and date_zkc >= dates[0]:
                if label_zkc > 0:
                    plt.axvline(x=date_zkc, color='green', linestyle='-.', linewidth=2)
                    label_zkc += 1
                else:
                    plt.axvline(x=date_zkc, color='green', linestyle='-.', linewidth=2,
                                label="ЗКЦ")
                    label_zkc += 1

    if dates_pgi and len(dates_pgi) > 0:
        label_pgi = 0
        for date_pgi in dates_pgi:
            if date_pgi <= dates[-1] and date_pgi >= dates[0]:
                if label_pgi > 0:
                    plt.axvline(x=date_zkc, color='k', linestyle='-.-', linewidth=2)
                    label_pgi += 1
                else:
                    plt.axvline(x=date_zkc, color='k', linestyle='-.-', linewidth=2,
                                label="ПГИ")
                    label_pgi += 1

    plt.axhline(y=0.85, color='grey', linestyle='--', linewidth=3.5)
    plt.ylabel("R2")
    plt.xlabel("dates")
    plt.title(well_num)
    plt.grid()
    plt.show()

    if not os.path.exists('plots\\Регрессия с окном %d с r2 больше 0.85' % window):
        os.makedirs('plots\\Регрессия с окном %d с r2 больше 0.85' % window)
    if not os.path.exists('plots\\Регрессия с окном %d с r2 больше 0.85\\Скважина %d' % (window, well_num)):
        os.makedirs('plots\\Регрессия с окном %d с r2 больше 0.85\\Скважина %d' % (window, well_num))
    path = 'plots\\Регрессия с окном %d с r2 больше 0.85\\Скважина %d\\' % (window, well_num)

    for inter in dict_with_intervals:
        slice_of_interval = 1
        for k in range(len(dict_with_intervals[inter]["x_best"])):
            regression(dict_with_intervals[inter]["x_best"][k], dict_with_intervals[inter]["y_best"][k], 'obv', 'qj', well_num, path, inter, slice_of_interval)
            slice_of_interval += 1
    print("Графики с наилучшими регрессиями с r2 > 0.85 сохранены в \"plots\\Регрессия с окном %d с r2 больше 0.85\\Скважина %d\"" % (
        window, well_num))

    for inter in dict_with_intervals:
        for k in range(len(dict_with_intervals[inter]["x_best"])):
            x_line, y_line = regression_line(dict_with_intervals[inter]["x_best"][k], dict_with_intervals[inter]["y_best"][k])
            plt.plot(x_line, y_line, "-", alpha = 0.5, color = "steelblue")
    plt.title(well_num)
    plt.grid()
    plt.xlabel("obv")
    plt.ylabel("qj")
    plt.show()
