from scipy.stats import shapiro
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd


def shapiro_wilk_test_for_normality(pitch_data, alpha=0.05):
    shapiro_results = {}
    pitch_data_clean = pitch_data[pitch_data['estimated_woba_using_speedangle'].notna() &
                                  pitch_data['pitch_type'].notna()]

    for pitch_type in pitch_data_clean['pitch_type'].unique():
        subset = pitch_data_clean[pitch_data_clean['pitch_type'] == pitch_type]['estimated_woba_using_speedangle']

        if len(subset) < 10:
            shapiro_results[pitch_type] = "Not enough data"
            continue

        stat, p_value = shapiro(subset)

        if p_value > alpha:
            shapiro_results[pitch_type] = "Normal"
        else:
            shapiro_results[pitch_type] = "Not normal"

    return shapiro_results


def calculate_median_woba_by_pitch_type(pitch_data):
    median_woba_by_pitch_type = {}
    pitch_data_clean = pitch_data[pitch_data['estimated_woba_using_speedangle'].notna() &
                                  pitch_data['pitch_type'].notna()]

    for pitch_type in pitch_data_clean['pitch_type'].unique():
        subset = pitch_data_clean[pitch_data_clean['pitch_type'] == pitch_type]['estimated_woba_using_speedangle']

        median_woba = subset.median()
        median_woba_by_pitch_type[pitch_type] = round(median_woba, 3)

    return median_woba_by_pitch_type


def calculate_ball_strike_ratio(pitch_data):
    strike_ball_regular = pitch_data[pitch_data['type'].notna(
    ) & pitch_data['pitch_type'].notna()]
    strike_ball_counts_regular = strike_ball_regular.groupby(['pitch_type', 'type']).size().unstack(fill_value=0)
    strike_ball_counts_regular['Total'] = strike_ball_counts_regular.sum(axis=1)
    strike_ball_counts_regular['Strike_Ball_Ratio'] = round(
        strike_ball_counts_regular['S'] / strike_ball_counts_regular['B'], 2)
    strike_ball_ratio_ranking_regular = strike_ball_counts_regular['Strike_Ball_Ratio'].sort_values(ascending=False)
    return strike_ball_ratio_ranking_regular.to_dict()


def run_linear_regression(pitch_data):
    features = ['release_speed', 'release_spin_rate', 'plate_x', 'plate_z', 'pfx_x', 'pfx_z']
    df_regular_season_clean = pitch_data.dropna(subset=features + ['estimated_woba_using_speedangle'])

    linear_models_rmse = {}
    linear_models_coefficients = {}

    for pitch_type in df_regular_season_clean['pitch_type'].unique():
        subset = df_regular_season_clean[df_regular_season_clean['pitch_type'] == pitch_type]

        if len(subset) < 10:
            continue

        X = subset[features]
        y = subset['estimated_woba_using_speedangle']

        model = LinearRegression()

        try:
            cross_val_scores = cross_val_score(model, X, y, cv=5, scoring='neg_root_mean_squared_error')
            rmse = np.mean(-cross_val_scores)
            linear_models_rmse[pitch_type] = rmse

            model.fit(X, y)
            linear_models_coefficients[pitch_type] = dict(zip(features, model.coef_))
        except:
            print(f"Failed to fit model for pitch type {pitch_type}")

    return linear_models_rmse, linear_models_coefficients


def statistical_analysis(pitch_data):
    test_for_normality = shapiro_wilk_test_for_normality(pitch_data)
    print(test_for_normality)
    # result shows pitch_type vs. estimated_woba_using_speedangle are not normally-distributed
    # visual inspection shows some right skewness
    # prefer median over mean
    pitch_type_median = calculate_median_woba_by_pitch_type(pitch_data)
    print(pitch_type_median)
    """
        SI    0.1980
        CH    0.2100
        FF    0.2255
        SL    0.2520
        KC    0.2850
        ... interpretation: sinker limits quality contact
    """
    pitch_type_ball_strike = calculate_ball_strike_ratio(pitch_data)
    print(pitch_type_ball_strike)
    """    
        FF    1.75
        SL    1.27
        KC    1.25
        SI    1.25
        CH    0.46
        ... interpretation: 4-seam fastball generates the most strikes proportionally, but...
        ANOVA Test Results:
            F-statistic: 0.104
            p-value: 0.981 (> 0.05 => differences in estimated_woba_using_speedangle across different pitch types are not statistically significant)
    """
    rmse, coeffs = run_linear_regression(pitch_data)
    print(rmse)
    print(coeffs)
    """
       Lower RMSE indicates a better fit to the data, meaning the model predicts estimated_woba_using_speedangle more accurately for that pitch type.        
            FF    0.432
            SI    0.405
            CH    0.569
            SL    0.395
            KC    0.553
        ... but RMSE is in terms of estimated_woba_using_speedangle... so this is pretty terrible
        Coefficients...
            FF (Fastball)
                Release Speed: 0.0045
                Release Spin Rate: 0.0002
                Plate X: 0.058
                Plate Z: -0.121 => lowering the pitch creates lower estimated_woba_using_speedangle
                Pfx X: -0.065 
                Pfx Z: -0.189 => more downward movement creates lower estimated_woba_using_speedangle
                INTERPRETATION: 
            SI (Sinker)
                Release Speed: -0.077 => lower speed results in lower estimated_woba_using_speedangle
                Release Spin Rate: 0.0014
                Plate X: -0.226
                Plate Z: 0.075 => higher pitches increase estimated_woba_using_speedangle
                Pfx X: -0.452
                Pfx Z: -0.565 => more downward movement creates lower estimated_woba_using_speedangle 
            CH (Changeup)
                Release Speed: 0.009
                Release Spin Rate: -0.0021
                Plate X: 0.393 => throwing more towards the center horizontally increases estimated_woba_using_speedangle
                Plate Z: -0.289
                Pfx X: -0.272
                Pfx Z: -0.598
            SL (Slider)
                Release Speed: 0.0036
                Release Spin Rate: 0.0002
                Plate X: 0.051
                Plate Z: 0.030
                Pfx X: 0.021
                Pfx Z: -0.206
            KC (Knuckle Curve)
                Release Speed: -0.030
                Release Spin Rate: 0.0007
                Plate X: -0.004
                Plate Z: 0.128
                Pfx X: 0.103
                Pfx Z: 0.057
        
        Generally...
        - FF more effective when thrown low
        - SI more effective at lower speeds and more downward
        - CH more effective when thrown low
    """
    print("break")
