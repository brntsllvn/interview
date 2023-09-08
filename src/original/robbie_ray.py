import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from pybaseball import playerid_lookup, statcast_pitcher

# Initialize player ID and fetch data
player_id = 592662
ray_stats = statcast_pitcher('2021-03-01', '2022-11-01', player_id)
ray_stats['year'] = pd.to_datetime(ray_stats['game_date']).dt.year
ray_stats.to_csv('ray.csv')
print("break")

# Filter out rows without pitch_type and 'estimated_woba_using_speedangle'
# ray_stats = ray_stats.dropna(subset=['pitch_type', 'estimated_woba_using_speedangle'])
ray_stats = ray_stats.dropna(subset=['pitch_type'])

# Features and stats
features = ['release_speed', 'release_spin_rate', 'pfx_x', 'pfx_z', 'plate_x', 'plate_z']
pitch_types = ray_stats['pitch_type'].unique()

# Frequency Data
pitch_frequency = ray_stats.groupby(['year', 'pitch_type']).size().reset_index(name='count')
total_pitches = pitch_frequency.groupby('year')['count'].transform('sum')
pitch_frequency['percent'] = (pitch_frequency['count'] / total_pitches) * 100

# wOBA calculations
woba_data = ray_stats.groupby(['year', 'pitch_type'])['estimated_woba_using_speedangle'].mean().reset_index()
woba_pivot = woba_data.pivot(index='pitch_type', columns='year',
                             values='estimated_woba_using_speedangle').fillna(0).round(3)

# Merge frequency and wOBA
merged_data = pd.merge(pitch_frequency, woba_data, how='outer', on=['year', 'pitch_type'])
merged_pivot = merged_data.pivot(index='pitch_type', columns='year', values=[
                                 'count', 'percent', 'estimated_woba_using_speedangle']).fillna(0)

# Page 1: Frequency Table + wOBA
fig1 = plt.figure(figsize=(11, 8.5))
ax1 = fig1.add_subplot(111)
ax1.axis('tight')
ax1.axis('off')

# Calculate Differences for Count and Percent
merged_pivot[('count', 'diff')] = merged_pivot[('count', 2022)] - merged_pivot[('count', 2021)]
merged_pivot[('percent', 'diff')] = merged_pivot[('percent', 2022)] - merged_pivot[('percent', 2021)]

# Reorder and Format
final_table = merged_pivot[[('count', 2021), ('count', 2022), ('count', 'diff'), ('percent', 2021),
                            ('percent', 2022), ('percent', 'diff'), ('estimated_woba_using_speedangle', 2021),
                            ('estimated_woba_using_speedangle', 2022)]].round({'count': 0, 'percent': 0, 'estimated_woba_using_speedangle': 3}).astype({'count': int, 'percent': int})

ax1.table(cellText=final_table.values, colLabels=final_table.columns,
          rowLabels=final_table.index, loc='center', fontsize=100)
# plt.savefig('FrequencyTable_WOBA.png')
final_table.to_csv('FrequencyTable_WOBA.csv')

for feature in features:
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(2, len(pitch_types), height_ratios=[3, 1], hspace=1, wspace=1)

    for j, pitch in enumerate(pitch_types):
        ax = plt.subplot(gs[0, j])

        # Boxplot
        subset_data = ray_stats[ray_stats['pitch_type'] == pitch]
        subset_data.boxplot(column=feature, by='year', ax=ax)

        # Table with statistical summary
        ax_table = plt.subplot(gs[1, j])
        stats_2021 = subset_data[subset_data['year'] == 2021][feature].describe().round(0)
        stats_2022 = subset_data[subset_data['year'] == 2022][feature].describe().round(0)
        stats_diff = stats_2022 - stats_2021
        table_data = pd.DataFrame({'2021': stats_2021, '2022': stats_2022, 'Diff': stats_diff})
        table_data = table_data.loc[['mean', '50%', 'min', 'max', 'std']].fillna(0)

        ax_table.axis('tight')
        ax_table.axis('off')
        ax_table.table(cellText=table_data.values, colLabels=table_data.columns,
                       rowLabels=table_data.index, loc='center', colWidths=[0.2]*3, fontsize=12)

        ax.set_title(f"{pitch}")
        ax.set_xlabel("")
        ax.set_ylabel("")

        if j == 0:
            ax.annotate(f"{feature}", xy=(0, 1.5), xycoords='axes fraction', fontsize=20, ha="center", va="center")

    plt.subplots_adjust(bottom=0.3)
    plt.savefig(f"{feature}_Metrics.png")
