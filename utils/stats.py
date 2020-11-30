import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
from io import BytesIO
import base64


def image_from_plt(fig):
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png', transparent=True)
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    return encoded


def get_week_stats(y_air, y_train):
    y_air = np.array(y_air)
    y_train = np.array(y_train)

    x = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    fig, ax = plt.subplots()
    ax.bar(x, y_air, width=0.7, label='Полеты')
    ax.bar(x, y_train, width=0.7, label='Поезда',bottom=y_air)
    ax.legend(prop={'size': 20})

    ax.set_facecolor('seashell')
    fig.set_figwidth(12)  # ширина Figure
    fig.set_figheight(6)  # высота Figure
    fig.set_facecolor('floralwhite')

    return image_from_plt(fig)


def get_range_stats(y_air, y_train):
    plt.clf()

    y_air = np.array(y_air)
    y_train = np.array(y_train)

    x = np.arange(len(y_air))
    x_new = np.linspace(0, len(y_air)-1, 200)
    spline_air = interpolate.make_interp_spline(x, y_air)
    spline_train = interpolate.make_interp_spline(x, y_train)

    y_air_new = spline_air(x_new)
    y_train_new = spline_train(x_new)

    plt.plot(x_new, y_air_new, label='Полеты')
    plt.plot(x_new, y_train_new, label='Поезда')
    plt.legend()
    ax = plt.gca()
    ax.yaxis.grid(True)
    ax.set_xticklabels([])

    return image_from_plt(plt)


def get_pie(bought_seats, free_seats):
    plt.clf()

    labels = 'Bought', 'Free'
    sizes = [bought_seats, free_seats]
    explode = (0, 0.4)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    return image_from_plt(fig1)
