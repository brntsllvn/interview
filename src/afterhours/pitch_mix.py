import matplotlib.pyplot as plt
from pandas.plotting import table


def create_pitch_mix_report(pitch_data, outfile):
    pitch_mix_data = pitch_data[['pitch_type', 'year']].dropna(subset=['pitch_type'])
    pitch_counts_by_year = pitch_mix_data.groupby(['year', 'pitch_type']).size().reset_index(name='count')
    pivot_table = pitch_counts_by_year.pivot(index='pitch_type', columns='year', values='count').fillna(0).reset_index()

    pivot_table['diff'] = pivot_table[2022] - pivot_table[2021]
    pivot_table['%_2021'] = (pivot_table[2021] / pivot_table[2021].sum()) * 100
    pivot_table['%_2022'] = (pivot_table[2022] / pivot_table[2022].sum()) * 100
    pivot_table['%_diff'] = pivot_table['%_2022'] - pivot_table['%_2021']
    pivot_table = pivot_table.rename(columns={'pitch_type': 'pitch'})
    pivot_table = pivot_table.sort_values(by='%_diff', ascending=False)

    formatted_table = pivot_table.copy()
    formatted_table[2021] = formatted_table[2021].apply(lambda x: '{:,}'.format(x))
    formatted_table[2022] = formatted_table[2022].apply(lambda x: '{:,}'.format(x))
    formatted_table['diff'] = formatted_table['diff'].astype(int)
    formatted_table['%_2021'] = formatted_table['%_2021'].round(0).astype(int).astype(str) + '%'
    formatted_table['%_2022'] = formatted_table['%_2022'].round(0).astype(int).astype(str) + '%'
    formatted_table['%_diff'] = formatted_table['%_diff'].round(0).astype(int).astype(str) + '%'
    markdown_text = formatted_table.to_markdown()
    print(markdown_text)

    # fig, ax = plt.subplots(figsize=(8, 6))
    # ax.axis('off')

    # formatted_table.reset_index(drop=True, inplace=True)

    # tab = table(ax, formatted_table, loc='center', cellLoc='left', colWidths=[0.1] * len(formatted_table.columns))
    # tab.auto_set_font_size(False)
    # tab.set_fontsize(12)
    # tab.scale(1.2, 1.2)

    # for key, cell in tab.get_celld().items():
    #     if key[0] == 0:
    #         cell.set_fontsize(12)
    #         cell.set_text_props(weight='bold')
    #     else:
    #         cell.set_fontsize(12)
    #         cell.set_text_props(ha='right')

    # plt.savefig(outfile, bbox_inches='tight', pad_inches=0.1, dpi=300)
