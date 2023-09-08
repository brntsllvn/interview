import seaborn as sns
import matplotlib.pyplot as plt


def swarm(regular_season_pitch_data):
    sns.set_theme(style="whitegrid", palette="muted")

    # Load the penguins dataset
    # df = sns.load_dataset("penguins")

    # Draw a categorical scatterplot to show each observation
    ax = sns.swarmplot(data=regular_season_pitch_data, x="release_speed", y="year", hue="pitch_type")
    ax.set(ylabel="")

    plt.savefig("./src/afterhours/swarm.png")
