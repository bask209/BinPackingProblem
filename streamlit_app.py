import streamlit as st
import pandas as pd
import sqlite3

documentation_string=r'''
Please, before using this software, have a look at the documentation following these links: 

[General apps documentation](https://vidabasca.com/appsyoucanuse)

[Bin packing problem documentation](https://vidabasca.com/appsyoucanuse/bin-packing-problem)
'''

st.write(documentation_string)

def chunk_list(input_list, chunk_size):
    chunked_list = []
    for item in input_list:
        while item > chunk_size:
            chunked_list.append(chunk_size)
            item -= chunk_size
        if item > 0:
            chunked_list.append(item)
    return chunked_list

def bestFit(weight, c):
    res = 0
    bin_rem = []

    for w in weight:
        min_space = c + 1
        bi = -1

        for j in range(res):
            if bin_rem[j] >= w and bin_rem[j] - w < min_space:
                bi = j
                min_space = bin_rem[j] - w

        if min_space == c + 1:
            bin_rem.append(c - w)
            res += 1
        else:
            bin_rem[bi] -= w

    non_zero_chunks = [element for element in bin_rem if element != 0]
    non_zero_chunks.sort(reverse=True)
    st.write('- Optimal Segments with Leftover Space: ', len(non_zero_chunks))
    st.write('- Optimal Leftover: ', sum(non_zero_chunks))

    return res

# Streamlit app
st.title('Bin Packing Optimization')

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'sqlite'])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]

    if file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension == 'xlsx':
        df = pd.read_excel(uploaded_file)
    elif file_extension == 'sqlite':
        conn = sqlite3.connect(uploaded_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_name = st.selectbox("Select the table", [table[0] for table in tables])
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)

    if df is not None:
        st.write(df)

        column = st.selectbox("Select the column for bin sizes", df.columns)

        # Detect column data type and find non-numeric rows if any
        if not pd.api.types.is_numeric_dtype(df[column]):
            st.write("Selected column is not numeric. Attempting to convert to numeric.")
            try:
                df[column] = pd.to_numeric(df[column], errors='raise')
                st.write("Conversion successful.")
            except ValueError:
                st.error("Conversion failed. The following rows contain non-numeric data:")
                non_numeric_rows = df[~df[column].apply(lambda x: pd.api.types.is_number(x))].index.tolist()
                st.write(df.loc[non_numeric_rows])
                st.stop()

        bin_size = st.number_input("Enter the bin size", min_value=0)

        if st.button("Calculate"):
            weights = df[column].tolist()
            chunked_weights = chunk_list(weights, bin_size)
            result = bestFit(chunked_weights, bin_size)
            st.write("Number of optimal bins required:", result)
            st.write("Number of highest amount of bins required:", len(chunked_weights))
