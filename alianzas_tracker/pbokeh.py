from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
from bokeh.models import HoverTool, ColumnDataSource
from datetime import datetime
from scrape_likes import get_likes

import pandas as pd


nid = "CERyIJrDX-k"
vid = "CERyEzBDLlm"
archivo = "log.pkl"
columnas = ["tiempo", "verde", "naranja", "diferencia"]
try:
    log = pd.read_pickle(archivo)
except FileNotFoundError:
    log = pd.DataFrame(columns=columnas)

source = ColumnDataSource(data=log)

p = figure(x_axis_type="datetime", sizing_mode="stretch_both")

# p.add_tools(CrosshairTool())
verde = p.line(
    "tiempo",
    "verde",
    source=source,
    color="green",
    line_width=5,
    legend_label="Alianza Verde",
    name="verde",
)

sverde = p.scatter(
    "tiempo",
    "verde",
    source=source,
    color="black",
    line_width=5,
    name="sverde",
)
p.add_tools(
    HoverTool(
        renderers=[verde],
        show_arrow=False,
        line_policy="next",
        tooltips=[
            ("Tiempo", "@tiempo{%R}"),
            ("Likes", "@verde{0,0}"),
        ],
        formatters={"@tiempo": "datetime"},
        mode="vline",
        names=["verde"],
    )
)
naranja = p.line(
    "tiempo",
    "naranja",
    source=source,
    color="orange",
    line_width=5,
    legend_label="Alianza Naranja",
    name="naranja",
)

snaranja = p.scatter(
    "tiempo",
    "naranja",
    source=source,
    color="black",
    line_width=5,
    name="snaranja",
)

p.add_tools(
    HoverTool(
        renderers=[naranja],
        show_arrow=False,
        line_policy="next",
        tooltips=[
            ("Likes", "@naranja{0,0}"),
        ],
        formatters={"@tiempo": "datetime"},
        mode="vline",
        names=["naranja"],
    )
)

p.legend.location = "top_left"
p.legend.click_policy = "hide"

likes_verde = verde.data_source
likes_naranja = naranja.data_source


@linear()
def update(step):
    print("owo")

    try:
        log = pd.read_pickle(archivo)
    except FileNotFoundError:
        log = pd.DataFrame(columns=columnas)

    tiempo = datetime.now()
    verde = get_likes(vid)
    naranja = get_likes(nid)
    diferencia = verde - naranja
    print(verde, naranja)

    fila = pd.DataFrame([[tiempo, verde, naranja, diferencia]], columns=columnas)
    log = log.append(fila, ignore_index=True)
    log.to_pickle(archivo)

    likes_verde.data = log
    likes_naranja.data = log

    likes_verde.trigger("data", likes_verde.data, likes_verde.data)
    likes_naranja.trigger("data", likes_naranja.data, likes_naranja.data)


curdoc().add_root(p)

# Add a periodic callback to be run every 45000 milliseconds
curdoc().add_periodic_callback(update, 60000)
