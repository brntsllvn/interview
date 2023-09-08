import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Ellipse
import numpy as np
import pandas as pd


def create_x_z_heatmaps(pitch_data, chart_title, x_metric, z_metric, outfile):
    pitch_types = pitch_data['pitch_type'].dropna().unique()

    num_rows = (len(pitch_types) + 1) // 2  # Ensure at least 1 row

    fig, axs = plt.subplots(num_rows, 2, figsize=(12, num_rows * 6))
    fig.subplots_adjust(hspace=0.5)  # Adjust vertical spacing

    if num_rows == 1:
        axs = axs.reshape(1, -1)

    for i, pitch_type in enumerate(pitch_types):
        if i >= num_rows * 2:  # Ensure we don't exceed the number of subplots
            break

        row = i // 2  # Calculate the row for the current pitch type

        df_2021 = pitch_data[(pitch_data['pitch_type'] == pitch_type) & (pitch_data['year'] == 2021)]
        df_2022 = pitch_data[(pitch_data['pitch_type'] == pitch_type) & (pitch_data['year'] == 2022)]

        # Calculate the column index based on even or odd pitch types
        col = i % 2

        if not df_2021.empty:
            sns.histplot(df_2021, x=x_metric, y=z_metric, bins=30, ax=axs[row, col], color='blue', alpha=0.5)
        if not df_2022.empty:
            sns.histplot(df_2022, x=x_metric, y=z_metric, bins=30, ax=axs[row, col], color='orange', alpha=0.5)

        axs[row, col].grid(False)

        axs[row, col].set_xlabel(x_metric)
        axs[row, col].set_ylabel(z_metric)

        if not df_2021.empty or not df_2022.empty:
            # dispersion ellipse
            for df, color, label in [(df_2021, 'blue', '2021'), (df_2022, '#000000', '2022')]:
                if not df.empty:
                    x_std, y_std = np.std(df[x_metric]), np.std(df[z_metric])
                    x_mean, y_mean = np.mean(df[x_metric]), np.mean(df[z_metric])
                    ellipse = Ellipse((x_mean, y_mean), width=x_std*2, height=y_std*2, edgecolor=color,
                                      facecolor='none', linestyle='--', linewidth=2, label=f"{label} Dispersion")
                    axs[row, col].add_patch(ellipse)

            axs[row, col].set_title(f'{pitch_type} - 2021 vs 2022')
            handles, labels = axs[row, col].get_legend_handles_labels()
            axs[row, col].legend(handles=handles, labels=labels, loc='lower left')
        else:
            fig.delaxes(axs[row, col])  # Remove empty subplot

    plt.suptitle(chart_title, fontsize=24, fontweight='bold')

    plt.savefig(outfile)
