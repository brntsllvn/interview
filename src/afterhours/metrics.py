import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

ALPHA = 0.5
COLOR_2021 = 'blue'
COLOR_2022 = 'orange'


def create_pitch_comparison_plot(pitch_type, data_2021, data_2022, ax, metric):
    data_2021_pitch = data_2021[data_2021['pitch_type'] == pitch_type]
    data_2022_pitch = data_2022[data_2022['pitch_type'] == pitch_type]

    sns.kdeplot(data=data_2021_pitch[metric], label='2021',
                ax=ax, fill=True, common_norm=False, alpha=ALPHA, color=COLOR_2021)
    sns.kdeplot(data=data_2022_pitch[metric], label='2022',
                ax=ax, fill=True, common_norm=False, alpha=ALPHA, color=COLOR_2022)

    median_2021 = round(data_2021_pitch[metric].median(), 3)
    median_2022 = round(data_2022_pitch[metric].median(), 3)

    formatted_median_2021 = '{:,}'.format(median_2021)
    formatted_median_2022 = '{:,}'.format(median_2022)

    ax.axvline(median_2021, color=COLOR_2021, linestyle='--', label=f'2021 Median: {median_2021:.1f}')
    ax.axvline(median_2022, color=COLOR_2022, linestyle='--', label=f'2022 Median: {median_2022:.1f}')

    pitch_count_2021 = round(data_2021_pitch[metric].count(), 0)
    pitch_count_2022 = round(data_2022_pitch[metric].count(), 0)

    formatted_pitch_count_2021 = '{:,}'.format(pitch_count_2021)
    formatted_pitch_count_2022 = '{:,}'.format(pitch_count_2022)

    ax.set_title(f'Pitch Type: {pitch_type}')
    ax.set_xlabel(metric)
    ax.set_ylabel('Density')

    ax.legend(loc='lower left', title='Year',
              labels=[f'2021 (Count: {formatted_pitch_count_2021}, Median: {formatted_median_2021})',
                      f'2022 (Count: {formatted_pitch_count_2022}, Median: {formatted_median_2022})'],
              bbox_to_anchor=(0.0, 0.0), bbox_transform=ax.transAxes)


def create_pitch_comparison_grid(pitch_data, metric, chart_title, output_file):
    data_2021 = pitch_data[pitch_data['year'] == 2021]
    data_2022 = pitch_data[pitch_data['year'] == 2022]
    unique_pitch_types = pitch_data['pitch_type'].unique()

    num_rows = len(unique_pitch_types) // 2 + len(unique_pitch_types) % 2
    fig, axes = plt.subplots(num_rows, 2, figsize=(12, 6 * num_rows + 2))
    fig.subplots_adjust(hspace=0.25)

    axes = axes.flatten()

    for i, pitch_type in enumerate(unique_pitch_types):
        if i < len(axes):
            create_pitch_comparison_plot(pitch_type, data_2021, data_2022, axes[i], metric)

    for i in range(len(unique_pitch_types), len(axes)):
        fig.delaxes(axes[i])

    plt.suptitle(chart_title, fontsize=24, fontweight='bold')
    plt.savefig(output_file)
