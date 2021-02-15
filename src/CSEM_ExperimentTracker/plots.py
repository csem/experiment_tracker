import plotly
import plotly.graph_objects as go
import plotly.express as px


def plots_epochs(
    df,
    keys,
    mode="lines+markers",
):
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
                    hovertemplate="Base Model {} \n".format(
                        None != df.loc[i, ("hyper", "path_base_model")].iloc[0]
                    )
                    + "Units {} \n".format(
                        df.loc[i, ("hyper", "number_of_units")].iloc[0]
                    )
                    + "Dropout {} \n".format(df.loc[i, ("hyper", "dropout")].iloc[0])
                    + "freeze {} \n".format(df.loc[i, ("hyper", "freeze")].iloc[0])
                    + "Date {} \n".format(i),
                    marker_color=px.colors.qualitative.Light24[idx],
                )
            )

    return fig
