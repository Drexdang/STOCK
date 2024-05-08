import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews


st.title('Stock Dashboard')
# Display header image
st.image("IMG_20240507_122849.jpg", width=100, use_column_width=False)
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

try:
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        st.warning("No data found for the given parameters.")
    else:
        fig = go.Figure()

        # Add candlestick trace
        fig.add_trace(go.Candlestick(x=data.index,
                                     open=data['Open'],
                                     high=data['High'],
                                     low=data['Low'],
                                     close=data['Close'],
                                     name='Candlestick'))

        # Add line trace for adjusted close
        fig.add_trace(go.Scatter(x=data.index,
                                 y=data['Adj Close'],
                                 mode='lines',
                                 name='Adjusted Close'))

        # Customize the layout
        fig.update_layout(title=ticker + ' Stock Price',
                          xaxis_title='Date',
                          yaxis_title='Price')

        st.plotly_chart(fig)

        # Price Movements
        with st.expander("Price Movements"):
            data2 = data.copy()
            data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
            data2.dropna(inplace=True)
            st.write(data2)
            annual_return = data2['% Change'].mean() * 252 * 100
            st.write('Annual Return Is ', annual_return, '%')
            stdev = np.std(data2['% Change']) * np.sqrt(252)
            st.write('Standard Deviation is', stdev * 100, '%')
            st.write('Risk Adj. Return is', annual_return / (stdev * 100))

        # Fundamental Data
        with st.expander("Fundamental Data"):
            key = "M8J26JM4Y742BXCD"  # Replace with your Alpha Vantage API key
            fd = FundamentalData(key, output_format="pandas")
            st.subheader('Balance Sheet')
            balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
            bs = balance_sheet.T[2:]
            bs.columns = list(balance_sheet.T.iloc[0])
            st.write(bs)
            st.subheader('Income Statement')
            income_statement = fd.get_income_statement_annual(ticker)[0]
            is1 = income_statement.T[2:]
            is1.columns = list(income_statement.T.iloc[0])
            st.write(is1)
            st.subheader('Cash Flow Statement')
            cash_flow = fd.get_cash_flow_annual(ticker)[0]
            cf = cash_flow.T[2:]
            cf.columns = list(cash_flow.T.iloc[0])
            st.write(cf)

        # Top 10 News
        with st.expander("Top 10 News"):
            sn = StockNews(ticker)
            df_news = sn.read_rss()
            for i in range(min(10, len(df_news))):
                st.subheader(f'News{i+1}')
                st.write(df_news['published'][i])
                st.write(df_news['title'][i])
                st.write(df_news['summary'][i])
                title_sentiment = df_news['sentiment_title'][i]
                st.write(f'Title Sentiment {title_sentiment}')
                news_sentiment = df_news['sentiment_summary'][i]
                st.write(f'News Sentiment {news_sentiment}')

except Exception as e:
    st.error(f"An error occurred: {e}")
        
        
        
        
        
        
        