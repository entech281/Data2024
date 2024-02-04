import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

st.set_page_config(layout="wide")
#docs https://streamlit-aggrid.readthedocs.io/en/docs/
# aggrid docs https://www.ag-grid.com/javascript-data-grid/getting-started/
#see https://github.com/PablocFonseca/streamlit-aggrid/blob/main/st_aggrid/__init__.py
#aggdrid documentation https://www.ag-grid.com/javascript-data-grid/grid-options/
#https://streamlit-aggrid.readthedocs.io/en/docs/GridOptionsBuilder.html
@st.cache_data
def load_data():
    df = pd.read_csv("281_2023_scouting_all.csv")
    return df

st.title("281 2023 Scouting Data")
df = load_data()

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(enabled=True,paginationAutoPageSize=True)
gb.configure_default_column(groupable="true",filterable="true")
gb.configure_grid_options(alwaysShowHorizontalScroll=True)
gb.configure_side_bar(filters_panel=True)

#configure columns
gb.configure_column(
    field='How many cones scored [Top]',
    header_name="Top Cones",
    type=["]numericColumn"]
)
gb.configure_column(
    field='Team Number',
    header_name="Team#",
    lockVisible=True
)
AgGrid(df,
       gridOptions=gb.build(),
       height=400,
       allow_unsafe_jscode=True,
       width="100%'",
        custom_css={ "#gridToolBar": { "padding-bottom": "0px !important", } }
)



