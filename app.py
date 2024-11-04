import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set the Streamlit page configuration
st.set_page_config(layout='wide', page_title='StartUp Analysis')

# Custom CSS for styling
st.markdown("""
    <style>
        /* Style for headers */
        .main-title { color: #4e73df; font-size: 48px; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .section-title { color: #2E86C1; font-size: 24px; font-weight: bold; margin-top: 20px; }
        .metric-container { display: flex; justify-content: space-around; margin-top: 20px; }
        /* Button styling */
        .stButton > button { background-color: #4CAF50; color: white; font-size: 16px; padding: 10px 20px; border: none; }
        .stButton > button:hover { background-color: #45a049; }
        /* Styling tables */
        .st-dataframe { border: 1px solid #ddd; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# Custom Title
st.markdown("<div class='main-title'>📊 Startup Funding Analysis Dashboard</div>", unsafe_allow_html=True)

# Load data
df = pd.read_csv('cleaned_startup_data.csv')
st.dataframe(df)

# Process date column and add month and year columns
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])

df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year


# Define function for overall analysis
def load_overall_analysis():
    st.markdown("<div class='section-title'>Overall Analysis</div>", unsafe_allow_html=True)

    # Display metrics in a grid
    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total = round(df['amount'].sum())
            st.metric('Total Investment', f"{total} cr")
        with col2:
            max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
            st.metric('Maximum Funding in a Startup', f"{max_funding} cr")
        with col3:
            avg_funding = round(df.groupby('startup')['amount'].sum().mean())
            st.metric('Average Investment', f"{avg_funding} cr")
        with col4:
            num_startups = df['startup'].nunique()
            st.metric('Number of Funded StartUps', num_startups)

    st.markdown("<div class='section-title'>Month on Month Investment</div>", unsafe_allow_html=True)
    selected_option = st.selectbox('Select type', ['Total', 'Count'])

    # Month to month investment plot
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['date'] = pd.to_datetime(temp_df[['year', 'month']].assign(day=1))

    # Ensure temp_df has data before plotting
    if not temp_df.empty:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(temp_df['date'], temp_df['amount'], color='#4e73df', marker='o')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Set format for date
        plt.xticks(rotation=90)
        ax.set_xlabel('Month-Year')
        ax.set_ylabel('Investment Amount' if selected_option == 'Total' else 'Number of Investments')
        st.pyplot(fig)
    else:
        st.write("No data available for the selected option.")


# Define function for displaying investor details
def load_investor_details(investor):
    st.markdown(f"<div class='section-title'>{investor} Investments Overview</div>", unsafe_allow_html=True)
    investor_df = df[df['investors'].fillna('').str.contains(investor)]

    if investor_df.empty:
        st.write("No investments found for this investor.")
        return  # Exit the function if no data is available
    last_5_df = investor_df.head()[
        ['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last_5_df)

    if investor_df['amount'].sum() == 0:
        st.write("No significant investment amounts found for this investor.")
        return

    col1, col2 = st.columns(2)
    with col1:
        big_series = investor_df.groupby('startup')[
            'amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Investments')
        st.dataframe(big_series)
        fig, ax = plt.subplots(figsize=(14,6))
        plt.xticks(rotation='vertical')
        ax.bar(big_series.index, big_series.values, color='#2E86C1')
        st.pyplot(fig)

    with col2:
        vertical_series = investor_df.groupby('vertical')['amount'].sum().sort_values(ascending=False)
        st.subheader('Sectors Invested In')

        # Limit the chart to the top 5 sectors and group the rest under "Other"
        top_n = 5
        if len(vertical_series) > top_n:
            top_sectors = vertical_series[:top_n]
            other_sectors = vertical_series[top_n:].sum()
            top_sectors['Other'] = other_sectors
        else:
            top_sectors = vertical_series

        fig1, ax1 = plt.subplots(figsize=(8, 6))  # Increase figure size
        ax1.pie(top_sectors, labels=top_sectors.index, autopct="%0.01f%%")
        plt.legend(loc="best")
        st.pyplot(fig1)

    # Additional sections
    col3, col4 = st.columns(2)

    with col3:
        stage_series = investor_df.groupby('round')['amount'].sum().sort_values(ascending=False)
        st.subheader('Investment Stages')

        # Limit the chart to the top 5 stages and group the rest under "Other"
        top_n = 5
        if len(stage_series) > top_n:
            top_stages = stage_series[:top_n]
            other_stages = stage_series[top_n:].sum()
            top_stages['Other'] = other_stages
        else:
            top_stages = stage_series

        fig2, ax2 = plt.subplots(figsize=(8, 6))  # Increase figure size
        ax2.pie(top_stages, labels=top_stages.index, autopct="%0.1f%%")
        plt.legend(loc="best")  # Display labels in a legend instead of on the chart
        st.pyplot(fig2)

    with col4:
        city_series = investor_df.groupby('city')['amount'].sum().sort_values(ascending=False)
        st.subheader('Cities Invested In')

        # Limit the chart to the top 5 cities and group the rest under "Other"
        top_n = 5
        if len(city_series) > top_n:
            top_cities = city_series[:top_n]
            other_cities = city_series[top_n:].sum()
            top_cities['Other'] = other_cities
        else:
            top_cities = city_series

        fig3, ax3 = plt.subplots(figsize=(8, 6))  # Increase figure size
        ax3.pie(top_cities, labels=top_cities.index, autopct="%0.01f%%")
        plt.legend(loc="best")  # Display labels in a legend instead of on the chart
        st.pyplot(fig3)

    year_series = df[df['investors'].fillna('').str.contains(investor)].groupby('year')['amount'].sum()
    st.subheader('Year-over-Year Investments')
    fig4, ax4 = plt.subplots(figsize=(14, 6))
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation='vertical')
    ax4.plot(year_series.index, year_series.values, color='#4e73df', marker='o')
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Investment Amount')
    st.pyplot(fig4)


# Define function for displaying startup details
def load_startup_details(startup):
    st.markdown(f"<div class='section-title'>{startup} Analysis</div>", unsafe_allow_html=True)
    startup_df = df[df['startup'] == startup]

    st.subheader('Startup Overview')
    st.dataframe(startup_df[['date', 'amount', 'vertical', 'city', 'round', 'investors']].sort_values(by='date',
                                                                                                      ascending=False))

    st.subheader('Funding Over Time')
    fig, ax = plt.subplots(figsize=(14,6))
    ax.plot(startup_df['date'], startup_df['amount'], marker='o', color='#2E86C1')
    ax.set_xlabel('Date')
    ax.set_ylabel('Funding Amount (in cr)')
    st.pyplot(fig)

    total_funding = startup_df['amount'].sum()
    unique_rounds = startup_df['round'].nunique()
    st.metric('Total Funding', f"{total_funding} cr")
    st.metric('Number of Funding Rounds', unique_rounds)

# Sidebar menu
st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select one', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()
elif option == 'StartUp':
    selected_startup = st.sidebar.selectbox('Select StartUp', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find StartUp Details')
    if btn1:
        load_startup_details(selected_startup)
else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(
        set(sum((item for item in df['investors'].str.split(',') if isinstance(item, list)), []))))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)