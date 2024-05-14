import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters
from utils import MAIN_QUERY



def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:


    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]


    #df = df.groupby([ 'master_product_id', 'product_name', 'master_category_id', 'subcategory_name']).first().reset_index()

    #df.mask(df.astype(object).eq('None')).dropna()

    df.dropna(axis=1, how='all', inplace=True)

    df = df.groupby([ 'master_product_id', 'product_name', 'master_category_id', 'category_name','subcategory_name']).first().reset_index()
    
    return df

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
#@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    #rows = [dict(row) for row in rows_raw]
    return rows_raw

df = run_query(MAIN_QUERY.replace('--commas', '"""')).to_dataframe()
df_inspect = df.copy()


st.title("Product Properties Dataframe (General)")

dynamic_filters = DynamicFilters(df=df, filters=['category_name','subcategory_name', 'product_name'])

dynamic_filters.display_filters(location='sidebar')

dynamic_filters.display_df()

st.title("Product Properties Dataframe (Busqueda profunda)")

with st.expander("Abrir busqueda profunda"):
    st.dataframe(filter_dataframe(df_inspect))

# st.write(
#     """
#     """
# )
#st.dataframe(filter_dataframe(df))

