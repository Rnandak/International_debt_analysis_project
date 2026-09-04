import pandas as pd 
import numpy as np
import streamlit as st
import mysql.connector
from sqlalchemy import create_engine
import plotly_express as px

st.header("Pandas Data Cleaning/EDA & Visualization Project")
st.set_page_config(layout="wide")
st.divider()


# Python method for initiating database connection 
def databaseconnector(dbname):
    return mysql.connector.connect(
        host='127.0.0.1',user='root',password='test1234',database=dbname,auth_plugin='mysql_native_password'
    )

# data cleaning using pandas begins here 
countryseriesmd = pd.read_csv(r"C:\Users\Nanda\OneDrive\Documents\International_Debt_analysis_dataset\Country_Series_Metadata.csv",encoding_errors="ignore")
#removing a redundant column
countryseriesmd.drop(columns='Type',inplace=True)

#pushing the data into database using pandas to_sql

engine = create_engine("mysql+pymysql://root:test1234@127.0.0.1:3306/intdebtdetails")
countryseriesmd.to_sql(name="countryseries",con=engine,if_exists="replace")

#All Countries data getting cleaned 
allCountriesdata = pd.read_csv(r"C:\Users\Nanda\OneDrive\Documents\International_Debt_analysis_dataset\IDS_ALLCountries_Data.csv",encoding_errors="ignore")
allCountriesdata.columns = (
    allCountriesdata.columns
      .str.strip()
      .str.replace(' ', '_')
      .str.replace('-', '_')
      .str.replace(r'[^0-9a-zA-Z_]+', '', regex=True)
)
years_col= [col for col in allCountriesdata.columns if col.isdigit()]
allCountriesdata.rename(columns={col: f"y{col}" for col in years_col}, inplace=True)
allCountriesdata.drop(columns=["Counterpart_Area_Name","Counterpart_Area_Code"],inplace=True)
allCountriesdata.drop(allCountriesdata.tail(5).index,inplace=True,axis=0)
allCountriesdata.fillna(0,inplace=True)
allCountriesdata.to_sql(name="allcountriesdata",con=engine,if_exists="replace")

#foot notes data 
footnotesMetadata = pd.read_csv(r"C:\Users\Nanda\OneDrive\Documents\International_Debt_analysis_dataset\IDS_FootNoteMetaData.csv",encoding_errors="ignore")
footnotesMetadata.columns = (
    footnotesMetadata.columns
      .str.strip()
      .str.replace(' ', '_')
      .str.replace('-', '_')
      .str.replace(r'[^0-9a-zA-Z_]+', '', regex=True)
)
footnotesMetadata.drop(columns='Type',axis=0,inplace=True)
footnotesMetadata.to_sql(name="footnotesmetadata",con=engine,if_exists="replace")

#series metadata 
seriesmetadata = pd.read_csv(r"C:\Users\Nanda\OneDrive\Documents\International_Debt_analysis_dataset\IDS_SeriesMetaData.csv",encoding="latin1",encoding_errors="ignore")
seriesmetadata.columns = (
    seriesmetadata.columns
      .str.strip()
      .str.replace(' ', '_')
      .str.replace('-', '_')
      .str.replace(r'[^0-9a-zA-Z_]+', '', regex=True)
)

seriesmetadata.fillna({"License_Type":'No License'}, inplace=True)
seriesmetadata.drop(columns="Dataset",axis=0,inplace=True)
seriesmetadata.fillna({"Limitations_and_exceptions":"No Data","General comments": "No Data"},inplace=True)
seriesmetadata.to_sql(name="seriesmetadata",con=engine,if_exists="replace")


#IDS Country meta data Processing 
countrydata = pd.read_csv(r"C:\Users\Nanda\OneDrive\Documents\International_Debt_analysis_dataset\IDS_CountryMetaData.csv",encoding='cp1252',encoding_errors="ignore")
countrydata.columns = (
    countrydata.columns
      .str.strip()
      .str.replace(' ', '_')
      .str.replace('-', '_')
      .str.replace(r'[^0-9a-zA-Z_]+', '', regex=True)
)

countrydata = countrydata[countrydata['Income_Group'].notna()]
countrydata.replace('Original chained constant price data are rescaled.','Not Applicable',inplace=True)
countrydata['National_accounts_base_year']=countrydata['National_accounts_base_year'].astype(str).str.split('/').str[-1]
countrydata = countrydata.fillna({"Other_groups": "Not Applicable"})
countrydata = countrydata.fillna({'Vital_registration_complete': 'No'})
countrydata[['Latest_industrial_data','Latest_trade_data','Latest_water_withdrawal_data']] =countrydata[['Latest_industrial_data','Latest_trade_data','Latest_water_withdrawal_data']].astype('object')
countrydata[['Latest_industrial_data','Latest_trade_data','Latest_water_withdrawal_data']] = countrydata[['Latest_industrial_data','Latest_trade_data','Latest_water_withdrawal_data']].apply(pd.to_numeric,errors='coerce').astype('Int64')
countrydata.to_sql(name='countrydata',con=engine,if_exists='replace')

st.divider()
st.title("Top 5 Countries with Highest External Debt")

qry = """with full_debt_details as (
select Country_Name,
`y2000`,
`y2001`,
`y2002`,
`y2003`,
`y2004`,
`y2005`,
`y2006`,
`y2007`,
`y2008`,
`y2009`,
`y2010`,
`y2011`,
`y2012`,
`y2013`,
`y2014`,
`y2015`,
`y2016`,
`y2017`,
`y2018`,
`y2019`,
`y2020`,
`y2021`,
`y2022`,
`y2023`,
`y2024`,
`y2025`,
`y2026`,
`y2027`,
`y2028`,
`y2029`,
`y2030`,
`y2031`,
`y2032`,
(`y2000`+
`y2001`+
`y2002`+
`y2003`+
`y2004`+
`y2005`+
`y2006`+
`y2007`+
`y2008`+
`y2009`+
`y2010`+
`y2011`+
`y2012`+
`y2013`+
`y2014`+
`y2015`+
`y2016`+
`y2017`+
`y2018`+
`y2019`+
`y2020`+
`y2021`+
`y2022`+
`y2023`+
`y2024`+
`y2025`+
`y2026`+
`y2027`+
`y2028`+
`y2029`+
`y2030`+
`y2031`+
`y2032`) as ttl
from allcountriesdata where Series_Code ='DT.DOD.DECT.CD')
select * from (
select *,row_number() over(order by ttl desc) as rnk 
from full_debt_details) as x where rnk<=5;"""

df = pd.read_sql_query(qry,databaseconnector("intdebtdetails"))
st.bar_chart(
    data=df,
    x="Country_Name",
    y="ttl",
    use_container_width=True
)
st.divider()

qry1 = """with full_debt_details as (
select Country_Name,
`y2000`,
`y2001`,
`y2002`,
`y2003`,
`y2004`,
`y2005`,
`y2006`,
`y2007`,
`y2008`,
`y2009`,
`y2010`,
`y2011`,
`y2012`,
`y2013`,
`y2014`,
`y2015`,
`y2016`,
`y2017`,
`y2018`,
`y2019`,
`y2020`,
`y2021`,
`y2022`,
`y2023`,
`y2024`,
`y2025`,
`y2026`,
`y2027`,
`y2028`,
`y2029`,
`y2030`,
`y2031`,
`y2032`,
(`y2000`+
`y2001`+
`y2002`+
`y2003`+
`y2004`+
`y2005`+
`y2006`+
`y2007`+
`y2008`+
`y2009`+
`y2010`+
`y2011`+
`y2012`+
`y2013`+
`y2014`+
`y2015`+
`y2016`+
`y2017`+
`y2018`+
`y2019`+
`y2020`+
`y2021`+
`y2022`+
`y2023`+
`y2024`+
`y2025`+
`y2026`+
`y2027`+
`y2028`+
`y2029`+
`y2030`+
`y2031`+
`y2032`) as ttl
from allcountriesdata where Series_Code ='DT.DOD.DECT.CD')
select * from (
select *,row_number() over(order by ttl asc) as rnk 
from full_debt_details) as x where rnk<=5;"""

st.title("Top 5 Countries with Lowest External Debt")

df1 = pd.read_sql_query(qry,databaseconnector("intdebtdetails"))
st.bar_chart(
    data=df1,
    x="Country_Name",
    y="ttl",
    use_container_width=True
)

qry2 = """
SELECT 
    Country_Name,
    (
        y2000 + y2001 + y2002 + y2003 + y2004 +
        y2005 + y2006 + y2007 + y2008 + y2009 +
        y2010 + y2011 + y2012 + y2013 + y2014 +
        y2015 + y2016 + y2017 + y2018 + y2019 +
        y2020 + y2021 + y2022 + y2023 + y2024 +
        y2025 + y2026 + y2027 + y2028 + y2029 +
        y2030 + y2031 + y2032
    ) AS ttl
FROM allcountriesdata
WHERE Series_Code IN (
    'DT.DOD.ALLC.CD');
"""

df2 = pd.read_sql_query(qry2, databaseconnector("intdebtdetails"))

st.subheader("Debt Distribution Across Regions")
fig = px.sunburst(
    df2,
    path=[ "Country_Name"],   # hierarchy
    values="ttl",
    title="Debt Distribution Across Regions",
    color="Country_Name",
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig.update_layout(
    margin=dict(t=50, l=25, r=25, b=25)
)

st.plotly_chart(fig, use_container_width=True, key="sunburst_chart")


import pandas as pd
import matplotlib.pyplot as plt

qry3 = """
SELECT Series_Name, Series_Code, y2020 AS Debt_Amount
FROM allcountriesdata
WHERE Country_Name = 'Equatorial Guinea'
AND y2020 IS NOT NULL
ORDER BY Debt_Amount DESC;
"""



# indicators bar chart
df3 = pd.read_sql_query(qry3,databaseconnector("intdebtdetails"))
fig = px.bar(
    df3,
    x="Series_Name",
    y="Debt_Amount",
    title="Debt Distribution Across Indicators – Country specific (2020)",
    color="Debt_Amount",
    color_continuous_scale="Teal",
)

fig.update_layout(
    height=900,                      # bigger chart
    width=1600,                      # wider chart
    font=dict(size=18),              # bigger text
    title_font=dict(size=28),        # bigger title
    xaxis_tickangle=-60,             # better readability
    xaxis=dict(tickfont=dict(size=16)),
    yaxis=dict(tickfont=dict(size=18)),
    margin=dict(l=80, r=80, t=120, b=200),
    coloraxis_colorbar=dict(
        title="Debt Amount",         # title is allowed
        tickfont=dict(size=16)       # tickfont is allowed
    )
)

st.plotly_chart(fig, use_container_width=True)

qry_trend = """
SELECT
    SUM(y2000) AS y2000,
    SUM(y2001) AS y2001,
    SUM(y2002) AS y2002,
    SUM(y2003) AS y2003,
    SUM(y2004) AS y2004,
    SUM(y2005) AS y2005,
    SUM(y2006) AS y2006,
    SUM(y2007) AS y2007,
    SUM(y2008) AS y2008,
    SUM(y2009) AS y2009,
    SUM(y2010) AS y2010,
    SUM(y2011) AS y2011,
    SUM(y2012) AS y2012,
    SUM(y2013) AS y2013,
    SUM(y2014) AS y2014,
    SUM(y2015) AS y2015,
    SUM(y2016) AS y2016,
    SUM(y2017) AS y2017,
    SUM(y2018) AS y2018,
    SUM(y2019) AS y2019,
    SUM(y2020) AS y2020,
    SUM(y2021) AS y2021,
    SUM(y2022) AS y2022
FROM allcountriesdata
WHERE Country_Name = 'India';
"""
df_trend = pd.read_sql_query(qry_trend, databaseconnector("intdebtdetails"))

df_trend_long = df_trend.T.reset_index()
df_trend_long.columns = ['Year', 'Debt']
df_trend_long['Year'] = df_trend_long['Year'].str.replace('y','').astype(int)

import plotly.express as px
fig = px.imshow(
    df_trend_long.pivot_table(index="Year", values="Debt"),
    labels=dict(x="Debt", y="Year", color="Debt Amount"),
    aspect="auto",
    color_continuous_scale="Viridis",
    title="Heatmap – International Debt Trends India (2000–2022)"
)

fig.update_layout(
    height=1000,                      # bigger chart
    width=100,                      # wider chart
    font=dict(size=18),              # bigger text
    title_font=dict(size=28),        # bigger title
    xaxis_tickangle=-60,             # better readability
    xaxis=dict(tickfont=dict(size=16)),
    yaxis=dict(tickfont=dict(size=18)),
    margin=dict(l=80, r=80, t=120, b=200),
    coloraxis_colorbar=dict(
        title="Debt Amount",         # title is allowed
        tickfont=dict(size=16)       # tickfont is allowed
    )
)
st.plotly_chart(fig)

st.header("SQL Queries")

st.write("Retrieve all distinct country names")
st.write("SELECT COUNT(DISTINCT Country_Name) AS Total_Countries FROM allcountriesdata;")
ds = pd.read_sql_query("SELECT DISTINCT Country_Name FROM allcountriesdata;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Count total number of countries")
st.write("SELECT COUNT(DISTINCT Country_Name) AS Total_Countries FROM allcountriesdata;")
ds = pd.read_sql_query("SELECT COUNT(DISTINCT Country_Name) AS Total_Countries FROM allcountriesdata;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("total number of indicators")
st.write("SELECT COUNT(DISTINCT Series_Name) AS Total_Indicators FROM allcountriesdata;")
ds = pd.read_sql_query("SELECT COUNT(DISTINCT Series_Name) AS Total_Indicators FROM allcountriesdata;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Display first 10 records ")
st.write("SELECT *FROM allcountriesdata LIMIT 10;")
ds = pd.read_sql_query("SELECT * FROM allcountriesdata LIMIT 10;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Calculate total global debt")
st.write("SELECT SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata;")
ds = pd.read_sql_query("SELECT SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("List all unique indicator names")
st.write("SELECT DISTINCT Series_Name FROM allcountriesdata;")
ds = pd.read_sql_query("SELECT DISTINCT Series_Name FROM allcountriesdata;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Number of records for each country")
st.write("SELECT Country_Name, COUNT(*) AS Record_Count FROM allcountriesdata GROUP BY Country_Name;")
ds = pd.read_sql_query("SELECT Country_Name, COUNT(*) AS Record_Count FROM allcountriesdata GROUP BY Country_Name;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Records where debt > 1 billion USD")
st.write("SELECT * FROM allcountriesdata WHERE y2000 > 1e9 OR y2001 > 1e9 OR y2002 > 1e9 OR y2003 > 1e9 OR y2004 > 1e9 OR y2005 > 1e9 OR y2006 > 1e9 OR y2007 > 1e9 OR y2008 > 1e9 OR y2009 > 1e9 OR y2010 > 1e9 OR y2011 > 1e9 OR y2012 > 1e9 OR y2013 > 1e9 OR y2014 > 1e9 OR y2015 > 1e9 OR y2016 > 1e9 OR y2017 > 1e9 OR y2018 > 1e9 OR y2019 > 1e9 OR y2020 > 1e9 OR y2021 > 1e9 OR y2022 > 1e9;")
ds = pd.read_sql_query("SELECT * FROM allcountriesdata WHERE y2000 > 1e9 OR y2001 > 1e9 OR y2002 > 1e9 OR y2003 > 1e9 OR y2004 > 1e9 OR y2005 > 1e9 OR y2006 > 1e9 OR y2007 > 1e9 OR y2008 > 1e9 OR y2009 > 1e9 OR y2010 > 1e9 OR y2011 > 1e9 OR y2012 > 1e9 OR y2013 > 1e9 OR y2014 > 1e9 OR y2015 > 1e9 OR y2016 > 1e9 OR y2017 > 1e9 OR y2018 > 1e9 OR y2019 > 1e9 OR y2020 > 1e9 OR y2021 > 1e9 OR y2022 > 1e9;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Min, Max, Avg debt")
st.write("SELECT * FROM allcountriesdata WHERE y2000 > 1e9 OR y2001 > 1e9 OR y2002 > 1e9 OR y2003 > 1e9 OR y2004 > 1e9 OR y2005 > 1e9 OR y2006 > 1e9 OR y2007 > 1e9 OR y2008 > 1e9 OR y2009 > 1e9 OR y2010 > 1e9 OR y2011 > 1e9 OR y2012 > 1e9 OR y2013 > 1e9 OR y2014 > 1e9 OR y2015 > 1e9 OR y2016 > 1e9 OR y2017 > 1e9 OR y2018 > 1e9 OR y2019 > 1e9 OR y2020 > 1e9 OR y2021 > 1e9 OR y2022 > 1e9;")
ds = pd.read_sql_query("SELECT * FROM allcountriesdata WHERE y2000 > 1e9 OR y2001 > 1e9 OR y2002 > 1e9 OR y2003 > 1e9 OR y2004 > 1e9 OR y2005 > 1e9 OR y2006 > 1e9 OR y2007 > 1e9 OR y2008 > 1e9 OR y2009 > 1e9 OR y2010 > 1e9 OR y2011 > 1e9 OR y2012 > 1e9 OR y2013 > 1e9 OR y2014 > 1e9 OR y2015 > 1e9 OR y2016 > 1e9 OR y2017 > 1e9 OR y2018 > 1e9 OR y2019 > 1e9 OR y2020 > 1e9 OR y2021 > 1e9 OR y2022 > 1e9;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Min, Max, Avg debt")
st.write("SELECT Min(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata; SELECT Max(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata; SELECT Avg(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata;")
ds = pd.read_sql_query("SELECT Min(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata; SELECT Max(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata; SELECT Avg(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt FROM allcountriesdata;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Count total number of records")
st.write("SELECT COUNT(*) AS Total_Records FROM allcountriesdata;")
ds = pd.read_sql_query("SELECT COUNT(*) AS Total_Records FROM allcountriesdata;", databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.divider()
st.header("Intermediate Queries")
st.write("Total debt for each country")
st.write("SELECT  Country_Name, SUM(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name;")
ds = pd.read_sql_query("SELECT  Country_Name, SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Country_Name;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Top 10 countries with highest total debt")
st.write("SELECT Country_Name,SUM(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;")
ds = pd.read_sql_query("SELECT  Country_Name, SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)


st.write("Top 10 countries with highest total debt")
st.write("SELECT Country_Name,SUM(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;")
ds = pd.read_sql_query("SELECT  Country_Name, SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Average debt per country")
st.write("SELECT Country_Name,AVG(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;")
ds = pd.read_sql_query("SELECT  Country_Name, AVG(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)   

st.write("Total debt for each indicator")
st.write("SELECT Series_Name,SUM(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;")
ds = pd.read_sql_query("SELECT  Series_Name,SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Series_Name ORDER BY Total_Debt DESC LIMIT 10;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)   

st.write("Indicator contributing highest total debt")
st.write("SELECT Series_Name,SUM(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;")
ds = pd.read_sql_query("SELECT  Series_Name,SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Series_Name ORDER BY Total_Debt DESC LIMIT 1;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)   

st.write("Country with lowest total debt")
st.write("SELECT Series_Name,SUM(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;")
ds = pd.read_sql_query("SELECT  Series_Name,SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Series_Name ORDER BY Total_Debt ASC LIMIT 1;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)  

st.write("Total debt for each country–indicator combination")
st.write("SELECT Country_Name,Series_Name,SUM(y2000 + y2001 + ... + y2022) AS Total_Debt FROM allcountriesdata GROUP BY Country_Name ORDER BY Total_Debt DESC LIMIT 10;")
ds = pd.read_sql_query("SELECT  Country_Name,Series_Name,SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Country_Name, Series_Name;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)  

st.write("Count indicators per country")
st.write("SELECT Country_Name,COUNT(DISTINCT Series_Name) AS Indicator_Count FROM allcountriesdata GROUP BY Country_Name;")
ds = pd.read_sql_query("SELECT Country_Name,COUNT(DISTINCT Series_Name) AS Indicator_Count FROM allcountriesdata GROUP BY Country_Name;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True) 

st.write("Countries whose total debt > global average")
st.write("WITH global_avg AS ( SELECT AVG(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS avg_debt FROM allcountriesdata) SELECT  Country_Name,SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Total_Debt FROM allcountriesdata, global_avg GROUP BY Country_Name HAVING Total_Debt > avg_debt;")
pd.read_sql_query("WITH global_avg AS ( SELECT AVG(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS avg_debt FROM allcountriesdata) SELECT  Country_Name,SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Total_Debt FROM allcountriesdata, global_avg GROUP BY Country_Name HAVING Total_Debt > avg_debt;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.write("Rank countries by total debt")
st.write("SELECT Country_Name, SUM(y2000 + y2001 + ... + y2022) AS Total_Debt,RANK() OVER (ORDER BY SUM(y2000 + y2001 + ... + y2022) DESC) AS Debt_Rank FROM allcountriesdata GROUP BY Country_Name;")
pd.read_sql_query("SELECT SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) as AS Total_Debt,RANK() OVER (ORDER BY SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) DESC) AS Debt_Rank FROM allcountriesdata GROUP BY Country_Name;" ",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)

st.divider()
st.header("Advanced Queries")
st.write("Top 5 indicators contributing most to global debt")
ds = pd.read_sql_query("SELECT  Series_Name,SUM(y2000 + y2001 + y2002 + y2003 + y2004 + y2005 + y2006 + y2007 + y2008 + y2009 + y2010 + y2011 + y2012 + y2013 + y2014 + y2015 + y2016 + y2017 + y2018 + y2019 + y2020 + y2021 + y2022) AS Global_Debt AS Total_Debt FROM allcountriesdata GROUP BY Series_Name ORDER BY Total_Debt DESC LIMIT 5;",databaseconnector("intdebtdetails"))
st.dataframe(ds,use_container_width=True)  









