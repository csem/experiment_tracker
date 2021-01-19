import plotly
import plotly.graph_objects as go


def epochs(df, key):
    fig = go.Figure()
    for i in set(df.index.get_level_values(0)):
        for j in set(df.loc[i].index.get_level_values(0)):
            fig.add_trace(
                go.Scatter(
                    x=list(df.loc[(i, j), "Validation_loss"].index),
                    y=list(df.loc[(i, j), "Validation_loss"]),
                    mode="markers",
                    name=str(i) + "_" + str(j),
                )
            )

    fig.update_yaxes(type="log")
    return fig
