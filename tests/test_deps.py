import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
from scipy.stats import zscore
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
from pybaseball import statcast
from pybaseball import pitching_stats  # fangraphs


def test_pandas():
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    assert df.shape == (2, 2)


def test_numpy():
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6


def test_matplotlib():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    plt.close(fig)


def test_sklearn():
    iris = load_iris()
    assert len(iris.data) == 150


def test_seaborn():
    sns.set()
    assert sns.get_dataset_names()[0] == 'anagrams'


def test_scipy():
    assert scipy.__version__


def test_pybaseball_statcast():
    cols = statcast(start_dt="2019-06-24", end_dt="2019-06-25").columns
    assert len(cols) == 92
    assert cols[0] == 'pitch_type'


def test_pybaseball_fangraphs():
    """
    If data.columns is empty or 1, then install from master...
    pip uninstall pybaseball
    pip install git+https://github.com/jldbc/pybaseball.git@master
    NOTE: Installing from master is volatile; the code can change frequently.
    """
    data = pitching_stats(2014, 2016)
    assert len(data.columns) == 334


def test_dep_integration():
    # Fetch statcast data for a specific date range
    data = statcast(start_dt='2021-06-01', end_dt='2021-06-07').dropna(subset=['launch_speed'])

    # Basic pandas operations: filter only needed columns and rows with 'launch_speed' > 0
    filtered_data = data[['player_name', 'launch_speed']]
    filtered_data = filtered_data[filtered_data['launch_speed'] > 0]
    filtered_data['launch_speed'] = filtered_data['launch_speed'].astype(float)

    print(filtered_data['launch_speed'].describe())
    print(np.sqrt(filtered_data['launch_speed']).describe())

    # Basic numpy operation: calculate the mean of 'launch_speed'
    mean_launch_speed = np.mean(filtered_data['launch_speed'])

    # Scikit-learn: Standardize the 'launch_speed' feature
    scaler = StandardScaler()
    filtered_data['scaled_launch_speed'] = scaler.fit_transform(filtered_data[['launch_speed']])

    # Seaborn: plot the distribution of original and scaled 'launch_speed'
    sns.set(style='whitegrid')
    plt.figure(figsize=(10, 6))
    sns.histplot(data=filtered_data, x='launch_speed', kde=True, label='Original')
    sns.histplot(data=filtered_data, x='scaled_launch_speed', kde=True, label='Scaled')

    # Scipy: Calculate the z-scores of 'launch_speed' and add as a new column
    filtered_data['zscore'] = zscore(filtered_data['launch_speed'])
    assert len(filtered_data.head()['player_name']) == 5
