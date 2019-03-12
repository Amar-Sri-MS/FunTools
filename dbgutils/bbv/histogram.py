#
#  histogram.py
#
#  Created by Hariharan Thantry on 2019-03-12
#
#  Copyright 2019 Fungible Inc. All rights reserved.
#

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class Histogram(object):
    def __init__(self):
        pass

    def plot(self, hist_map, hist_cols, lbl_arr, 
            title, out_png=None):
        # This loads in the key-value pairs into a Panda dataframe
        a4_dims = (20, 12)
        fig, ax = plt.subplots(figsize=a4_dims)
        df = pd.DataFrame(list(hist_map.items()), columns=hist_cols)

        sns.set_context("paper")
        sns.set_style("whitegrid")

        sns_plot = sns.barplot(x=hist_cols[0],
                       y=hist_cols[1],
                       data=df,
                    ax=ax
                    )

        sns_plot.set(xlabel=lbl_arr[0],
                ylabel=lbl_arr[1],
                Title=title)
        self.__show_on_bars(ax)
        if out_png:
            fig.savefig(out_png)
        else:
            plt.show()
    
    def __show_on_bars(self, axs):
        for p in axs.patches:
            _x = p.get_x() + p.get_width()/2
            _y = p.get_y() + p.get_height()
            val = '{}'.format(int(p.get_height()))
            axs.text(_x, _y, val, ha="center")

if __name__ == '__main__':
    p = Histogram()
    p.plot({0:20, 1:40, 2:25},
            ['x_val', 'y_val'],
            ['x_lbl', 'y_lbl'],
            "Test app",
            "test.png")



