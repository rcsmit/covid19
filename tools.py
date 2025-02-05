#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Small, generic helper functions.

- pause_commandline(): prompt user to continue (when outside Spyder).
- set_xaxis_dateformat(): set layout parameters for date x-axis.
"""
import os
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

def pause_commandline(msg='Press Enter to continue.'):
    """Prompt user to continue (when outside Spyder).

    Only do this script appears to be run from command line.
    This is to prevent plot windows from closing at program termination.
    """

    if 'SPYDER_ARGS' not in os.environ:
        input(msg)


def set_xaxis_dateformat(ax, xlabel=None, maxticks=10, yminor=False, ticklabels=True):
    """Set x axis formatting for dates; call after adjusting ranges etc."""


    md = matplotlib.dates
    date_lo, date_hi = pd.to_datetime(md.num2date(ax.get_xlim()))
    day_span = (date_hi - date_lo).days

    monday_locator = md.WeekdayLocator(0)

    minor_grid = False
    if day_span <= maxticks:
        ax.xaxis.set_major_locator(md.DayLocator())
        fmt = '%a %Y-%m-%d'
    elif day_span <= maxticks*7:
        ax.xaxis.set_major_locator(monday_locator)
        ax.xaxis.set_minor_locator(md.DayLocator())
        fmt = '%a %Y-%m-%d'
        minor_grid=True
    elif day_span <= maxticks*30.5:
        ax.xaxis.set_major_locator(md.MonthLocator())
        ax.xaxis.set_minor_locator(monday_locator)
        ax.tick_params('x', which='minor', direction='in')
        fmt = '%Y-%m-%d'
        if day_span <= maxticks*25:
            minor_grid = True
    else:
        ax.xaxis.set_major_locator(md.MonthLocator([1, 4, 7, 10]))
        ax.xaxis.set_minor_locator(md.MonthLocator())
        fmt = '%Y-%m-%d'
        minor_grid = (day_span < maxticks*90)


    ax.grid(which='major', axis='both', color='black', alpha=0.2)
    if minor_grid:
        ax.grid(which='minor', axis='x', color='black', alpha=0.1)

    if yminor:
        ax.grid(which='minor', axis='y', color='black', alpha=0.1)

    # ax.grid(which=('both' if minor_grid else 'major'))

    if ticklabels:
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(fmt))
        plt.xticks(rotation=-20)
        for tl in ax.get_xticklabels():
            tl.set_ha('left')

    if xlabel:
        ax.set_xlabel(xlabel)


def _test_set_xaxis_dateformat():
    date1 = pd.to_datetime('2010-05-03')
    date2s = ['2010-05-20', '2010-07-01', '2010-11-01', '2012-01-01']
    fig, axs = plt.subplots(len(date2s), 1, figsize=(10, 8))

    for date2, ax in zip(date2s, axs):
        date2 = pd.to_datetime(date2)
        tseries = pd.Series([0, 0], index=[date1, date2])
        ax.plot(tseries)
        set_xaxis_dateformat(ax, maxticks=5)
        fig.show()


def set_dense_minor_yticks(ax):
    """If axis y range is less than 2 decades: override y ticks to include 1.5."""
    ymin, ymax = ax.get_ylim()
    if ymax/ymin > 100:
        return
    emin = np.floor(np.log10(ymin/4))
    emax = np.ceil(np.log10(ymax*4))
    mticks = np.array([1.5, 2, 3, 4, 5, 6, 7, 8, 9])
    mticks = mticks * (10**np.arange(emin, emax).reshape(-1, 1))
    mticks = mticks[(mticks > ymin/4) & (mticks < ymax*4)]
    ax.yaxis.set_ticks(mticks, minor=True)
    ax.set_ylim(ymin, ymax)


def set_yaxis_log_minor_labels(ax):
    """Set minor tick labels on log scale, including 1.5.

    Tick 6 and 8 will have no label.

    Call this after adding all the data and optionally setting y-range.
    """
    import matplotlib.ticker as mt

    class MyLogFormatter(mt.LogFormatter):
        """Use SI prefixes for large values."""
        def __call__(self, x, pos=None):
            mantisse = np.around(x* 10 ** -np.floor(np.log10(x)), 1)
            if mantisse in (6, 8, 9):
                return ''
            for mul, prefix in [(1e6, 'M'), (1e3, 'k'), (1, ''), (1e-3, 'm')]:
                if x >= mul:
                    break
            return f'{x/mul:.3g}{prefix}'

    formatter = MyLogFormatter(minor_thresholds=(2, 1))
    ax.yaxis.set_minor_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    set_dense_minor_yticks(ax)


if __name__ == '__main__':

    _test_set_xaxis_dateformat()
