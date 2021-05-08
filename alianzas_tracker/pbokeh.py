from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
from bokeh.models import HoverTool, ColumnDataSource
from datetime import datetime, timedelta
from scrape_likes import get_likes

import pandas as pd

def predict_3h(df):
    if len(df["naranja"]) < 15 or len(df["verde"]) < 15:
        return pd.DataFrame()
    
    i_naranja = df["naranja"].iloc[-6]
    i_verde = df["verde"].iloc[-6]
    f_naranja = df["naranja"].iloc[-1]
    f_verde = df["verde"].iloc[-1]
    f_fecha = df["tiempo"].iloc[-1]

    m_naranja = (f_naranja - i_naranja)/5
    m_verde = (f_verde - i_verde)/5

    print("m naranja:", m_naranja, "m_verde:", m_verde)

    delta = timedelta(minutes=1)
    
    prediccion = pd.DataFrame()
    for x in range(1,181):
        delta = timedelta(minutes=x)
        tiempo = f_fecha + delta
        
        naranja = f_naranja + m_naranja*x
        verde = f_verde + m_verde*x

        fila = pd.DataFrame([[tiempo, verde, naranja]], columns=['tiempo', 'verde', 'naranja'])
        prediccion = prediccion.append(fila, ignore_index=True)
    
    return prediccion


nid = "CERyIJrDX-k"
vid = "CERyEzBDLlm"
archivo = "log.pkl"
columnas = ["tiempo", "verde", "naranja", "diferencia"]
try:
    log = pd.read_pickle(archivo)
except FileNotFoundError:
    log = pd.DataFrame(columns=columnas)

source = ColumnDataSource(data=log)
psource = ColumnDataSource(data=predict_3h(log))

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

# sverde = p.scatter(
#     "tiempo",
#     "verde",
#     source=source,
#     color="black",
#     line_width=5,
#     name="sverde",
# )

pverde = p.line(
    "tiempo",
    "verde",
    source=psource,
    color="green",
    line_width=2,
    name="pverde",
    line_dash = "dashed"
)

p.add_tools(
    HoverTool(
        renderers=[verde, pverde],
        show_arrow=False,
        line_policy="next",
        tooltips=[
            ("Tiempo", "@tiempo{%R}"),
            ("Likes", "@verde{0,0}"),
        ],
        formatters={"@tiempo": "datetime"},
        mode="vline",
        names=["verde", "pverde"],
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

pnaranja = p.line(
    "tiempo",
    "naranja",
    source=psource,
    color="orange",
    line_width=5,
    name="pnaranja",
    line_dash = "dashed"
)

# snaranja = p.scatter(
#     "tiempo",
#     "naranja",
#     source=source,
#     color="black",
#     line_width=2,
#     name="snaranja",
# )

p.legend.location = "top_left"
p.legend.click_policy = "hide"

likes_verde = verde.data_source
likes_naranja = naranja.data_source
plikes_verde = pverde.data_source
plikes_naranja = pnaranja.data_source


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
    
    prediccion = predict_3h(log)

    plikes_verde.data = prediccion
    plikes_naranja.data = prediccion

    likes_verde.trigger("data", likes_verde.data, likes_verde.data)
    likes_naranja.trigger("data", likes_naranja.data, likes_naranja.data)
    plikes_verde.trigger("data", plikes_verde.data, plikes_verde.data)
    plikes_naranja.trigger("data", plikes_naranja.data, plikes_naranja.data)



curdoc().add_root(p)

# Add a periodic callback to be run every 45000 milliseconds
curdoc().add_periodic_callback(update, 60000)
