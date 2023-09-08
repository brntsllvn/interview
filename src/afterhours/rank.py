
import pandas as pd
import numpy as np
from scipy.stats import shapiro, skew, kurtosis
import matplotlib.pyplot as plt
import seaborn as sns


def bootstrap_mean(data, n_bootstrap_samples=10000):
    bootstrap_means = []
    n = len(data)
    for _ in range(n_bootstrap_samples):
        bootstrap_sample = np.random.choice(data, size=n, replace=True)
        bootstrap_means.append(np.mean(bootstrap_sample))
    return bootstrap_means


def bootstrap_median(data, n_bootstrap_samples=10000):
    bootstrap_medians = []
    n = len(data)
    for _ in range(n_bootstrap_samples):
        bootstrap_sample = np.random.choice(data, size=n, replace=True)
        bootstrap_medians.append(np.median(bootstrap_sample))
    return bootstrap_medians


def rank_pitches_by_year(pitch_data, chart_title, output_file):
    filtered_data = pitch_data[pitch_data['delta_run_exp'].notna()]

    bootstrap_cis_by_year = {}
    normality_tests = {}
    for (pitch_type, year), group_data in filtered_data.groupby(['pitch_type', 'year']):
        pitch_data = group_data['delta_run_exp']
        if len(pitch_data) < 30:
            continue

        shap_w, shap_p = shapiro(pitch_data)
        skew_value = skew(pitch_data)
        kurt_value = kurtosis(pitch_data)
        normality_tests[f"{pitch_type}_{year}"] = {
            'Shapiro-Wilk': (shap_w, shap_p), 'Skewness': skew_value, 'Kurtosis': kurt_value}

        bootstrap_medians = bootstrap_median(pitch_data)
        lower = np.percentile(bootstrap_medians, 2.5)
        upper = np.percentile(bootstrap_medians, 97.5)
        median_value = np.median(bootstrap_medians)
        bootstrap_cis_by_year[f"{pitch_type}_{year}"] = {'Lower': lower, 'Upper': upper, 'Median': median_value}

    bootstrap_cis_95_df = pd.DataFrame.from_dict(bootstrap_cis_by_year, orient='index')
    bootstrap_cis_95_df.reset_index(inplace=True)
    bootstrap_cis_95_df[['Pitch_Type', 'Year']] = bootstrap_cis_95_df['index'].str.split('_', expand=True)
    bootstrap_cis_95_df.drop(columns=['index'], inplace=True)
    bootstrap_cis_95_df.sort_values('Lower', ascending=True, inplace=True)

    colors = {
        'FF': ['darkorange', 'orange'],
        'SI': ['darkblue', 'blue'],
        'SL': ['darkgreen', 'green'],
        'CH': ['darkred', 'red'],
        'KC': ['darkviolet', 'violet']
    }

    plt.figure(figsize=(12, 10))
    legend_labels = []
    for idx, row in bootstrap_cis_95_df.iterrows():
        color = colors.get(row['Pitch_Type'], 'grey')
        plt.plot([row['Lower'], row['Upper']], [row['Pitch_Type'] + ' ' + str(row['Year'])] * 2,
                 marker='o', linestyle='-', linewidth=2, color=color[0 if row['Year'] == '2021' else 1])
        legend_labels.append(f"{row['Pitch_Type']} {row['Year']} (Median={row['Median']:.3f})")

    plt.axvline(x=0, color='r', linestyle='--')
    plt.xlabel('delta_run_exp')
    plt.ylabel('Pitch Type and Year')
    plt.title('95% Bootstrap Confidence Intervals for delta_run_exp by Pitch Type and Year')
    plt.grid(True)
    plt.legend(legend_labels, title="Median", loc='lower right')
    plt.suptitle(chart_title, fontsize=24, fontweight='bold')
    plt.savefig(output_file)

    return normality_tests
