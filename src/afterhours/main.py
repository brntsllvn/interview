from metrics import create_pitch_comparison_grid
from heatmaps import create_x_z_heatmaps
from pitch_mix import create_pitch_mix_report
from stats import statistical_analysis
from rank import rank_pitches_by_year
from swarm import swarm

import pandas as pd
from pybaseball import statcast_pitcher


def output_file(player_id, metric):
    output_dir_prefix = './src/afterhours'
    return f'{output_dir_prefix}/{player_id}/{metric}.png'


def get_title(metric):
    return f'robbie ray - {metric.replace("_"," ")} - 2021-2022'.upper()


def main():
    robbie_ray_player_id = 592662
    pitch_data = statcast_pitcher('2021-03-01', '2022-11-01', robbie_ray_player_id)
    pitch_data['year'] = pd.to_datetime(pitch_data['game_date']).dt.year
    regular_season_pitch_data = pitch_data[pitch_data['game_type'] == 'R']

    pitch_mix_outfile = output_file(robbie_ray_player_id, "pitch_mix")
    create_pitch_mix_report(regular_season_pitch_data, pitch_mix_outfile)

    velocity_metric = "release_speed"
    velocity_title = get_title(velocity_metric)
    velocity_output_file = output_file(robbie_ray_player_id, velocity_metric)
    create_pitch_comparison_grid(regular_season_pitch_data, velocity_metric, velocity_title, velocity_output_file)

    spin_metric = "release_spin_rate"
    spin_title = get_title(spin_metric)
    spin_output_file = output_file(robbie_ray_player_id, spin_metric)
    create_pitch_comparison_grid(regular_season_pitch_data, spin_metric, spin_title, spin_output_file)

    xwoba_metric = "estimated_woba_using_speedangle"
    xwoba_title = get_title(xwoba_metric)
    xwoba_output_file = output_file(robbie_ray_player_id, xwoba_metric)
    create_pitch_comparison_grid(regular_season_pitch_data, xwoba_metric, xwoba_title, xwoba_output_file)

    delta_re_metric = "delta_run_exp"
    delta_re_title = get_title(delta_re_metric)
    delta_re_output_file = output_file(robbie_ray_player_id, delta_re_metric)
    create_pitch_comparison_grid(regular_season_pitch_data, delta_re_metric, delta_re_title, delta_re_output_file)

    plate_title = "plate_dispersion_heatmap"
    plate_presentation_title = get_title(plate_title)
    plate_dispersion_heatmaps_output_file = output_file(robbie_ray_player_id, plate_title)
    create_x_z_heatmaps(regular_season_pitch_data, plate_presentation_title,
                        "plate_x", "plate_z", plate_dispersion_heatmaps_output_file)

    movement_title = "pitch_movement_heatmap"
    movement_presentation_title = get_title(movement_title)
    pitch_movement_heatmaps_output_file = output_file(robbie_ray_player_id, movement_title)
    create_x_z_heatmaps(regular_season_pitch_data, movement_presentation_title,
                        "pfx_x", "pfx_z", pitch_movement_heatmaps_output_file)

    pitch_rank_metric = "pitch_rank"
    rank = rank_pitches_by_year(regular_season_pitch_data, "pitch_rank",
                                output_file(robbie_ray_player_id, pitch_rank_metric))
    print("break")


if __name__ == "__main__":
    main()
