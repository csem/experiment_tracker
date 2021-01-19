import plotly
import plotly.graph_objects as go
import plotly.express as px


def plots_epochs(df, keys, mode="lines+markers"):
    fig = go.Figure()
    if type(keys) != list:
        keys = [keys]
    for j in keys:
        for idx, i in enumerate(set(df.index.droplevel(-1))):
            fig.add_trace(
                go.Scatter(
                    x=list(df.loc[i, j].index),
                    y=list(df.loc[i, j]),
                    mode=mode,
                    name=str(j),
                    hovertemplate=str(df.loc[i, "hyper"].iloc[0]),
                    marker_color=px.colors.qualitative.Plotly[idx],
                )
            )

    return fig
