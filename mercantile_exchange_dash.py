import pandas as pd
import datetime as dt
#import pandas_datareader as web
import mplfinance as mpl
import datetime as dt
#import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

#----------------------1. IMPORT DATA ---------------------------------------

## ------1.1. Dữ liệu----------------------------

# Định nghĩa hàm để đọc dữ liệu
@st.cache_data
def load_data(file_path):
    # Đọc dữ liệu từ tệp Excel
    df = pd.read_excel(file_path)

    # Chuyển các cột 'Ngày dữ liệu', 'Ngày đặt lệnh', 'Ngày giờ thực hiện' về kiểu datetime
    # Chuyển đổi cột 'Ngày dữ liệu' sang datetime và hiển thị theo định dạng '%d/%m/%Y'
    # Chuyển đổi định dạng của cột 'Ngày dữ liệu' sang datetime
    df['Ngày dữ liệu'] = pd.to_datetime(df['Ngày dữ liệu'], format='%d/%m/%Y')

    # Sắp xếp DataFrame theo cột 'Ngày dữ liệu'
    df= df.sort_values(by='Ngày dữ liệu')

    # Chuyển đổi cột 'Ngày đặt lệnh' sang datetime và hiển thị theo định dạng '%d/%m/%Y'
    df['Ngày đặt lệnh'] = pd.to_datetime(df['Ngày đặt lệnh'], format='%d/%m/%Y')

    # Chuyển đổi cột 'Ngày giờ thực hiện' sang datetime và hiển thị theo định dạng '%d/%m/%Y %H:%M:%S'
    df['Ngày giờ thực hiện'] = pd.to_datetime(df['Ngày giờ thực hiện'], format='%d/%m/%Y %H:%M:%S')
    
    
    df = df[df['Nhóm hàng hóa'] == 'Năng lượng']
    df['Giá trị giao dịch'] = df['Giá trị giao dịch'] / 1e9
    
    return df

#file_path_df = "https://github.com/thuthuy119/mercantile_exchange_dash/blob/main/Data_MXV_T1-4_2024_(2).xlsx"
file_path_df = "Data_MXV_T1-4_2024_(2).xlsx"

df = load_data(file_path_df)

#----------------------------- 2. BUILDING APPLICATON---------------------------


st.markdown("<h2 style='font-weight: bold;text-align: center; color:firebrick;'>BÁO CÁO GIAO DỊCH CÁC MẶT HÀNG NĂNG LƯỢNG TRÊN MXV </h2>", unsafe_allow_html=True)

## ----------------------------Navigation panel --------------------------------


# Tạo sidebar
st.sidebar.title('')
st.sidebar.markdown("<h3 style='font-weight: bold;color:#AD2A1A;'>Selection bar</h3>", unsafe_allow_html=True)

# Lấy danh sách các ngày từ cột 'Ngày dữ liệu' đã được sắp xếp
list_of_dates = df['Ngày dữ liệu'].unique()

list_of_dates = [pd.to_datetime(date_str, format='%d/%m/%Y') for date_str in list_of_dates]

# Function to format dates as dd/mm/yyyy
def format_date(date):
    return date.strftime('%d/%m/%Y')

# Display the select slider with the specified date format
st.sidebar.markdown("<br><h5 style='font-weight: bold;color:#AD2A1A;'>Thời gian</h5>", unsafe_allow_html=True)
start_date, end_date = st.sidebar.select_slider(
    ' ',  # Dấu cách để giữ cho thanh trượt không bị mất nhãn
    options=list_of_dates,
    value=(list_of_dates[0], list_of_dates[-1]),
    format_func=format_date
)
# Lọc dataframe theo ngày
df = df[(df['Ngày dữ liệu'] >= start_date) & (df['Ngày dữ liệu'] <= end_date)]

# Chọn hàng hóa
st.sidebar.markdown("<br><h5 style='font-weight: bold;color:#AD2A1A;'>Hàng hóa</h5>", unsafe_allow_html=True)

product = st.sidebar.selectbox(
    ' ',  # Dấu cách để giữ cho thanh trượt không bị mất nhãn
    df['Hàng hóa'].unique(), 
    index=0,  # Chọn hàng hóa ban đầu
    format_func=lambda x: 'Dầu WTI' if x == 'Dầu WTI' else x  # Đảm bảo Dầu WTI là mặc định
)

# Lọc dataframe theo hàng hóa
df_filtered = df[df['Hàng hóa'] == product]


# Phân tích kỹ thuật
with st.expander("Phân tích kỹ thuật"):
    # Sử dụng st.markdown để chèn HTML
    #st.markdown("<h3 style='font-weight: bold;color:#AD2A1A;'>Phân tích kỹ thuật</h3>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='font-weight: bold;color:#AD2A1A;'>Phân tích kỹ thuật mặt hàng {product}</h5>", unsafe_allow_html=True)

    # Sắp xếp theo thời gian trong cột 'Ngày giờ thực hiện'
    df_filtered= df_filtered[df_filtered['Loại giao dịch'] == 'Futures']
    df_filtered = df_filtered.sort_values(by='Ngày giờ thực hiện')

    # Groupby 'Ngày dữ liệu' và 'Hàng hóa', sau đó tính các giá trị mong muốn
    df_candle_hh = df_filtered.groupby(['Ngày dữ liệu', 'Hàng hóa']).agg({
        'Giá khớp': ['first', 'last', 'max', 'min'],
        'KL giao dịch mua': ['sum'],
        'KL giao dịch bán': ['sum'],
        'Giá trị giao dịch': ['sum']
    }).reset_index()

    # Đặt lại tên cột
    df_candle_hh.columns = ['Ngày dữ liệu', 'Hàng hóa', 'Open', 'Close', 'High', 'Low', 'KL giao dịch mua', 'KL giao dịch bán', 'Giá trị giao dịch']

    # Chuyển cột thời gian thành index kiểu DatetimeIndex
    df_candle_hh.index = pd.to_datetime(df_candle_hh['Ngày dữ liệu'])

    # Xóa cột 'Ngày giờ thực hiện' nếu không cần thiết
    df_candle_hh.drop(columns=['Ngày dữ liệu'], inplace=True)

    # Đổi tên cột 'Giá trị giao dịch' thành 'Volume'
    df_candle_hh.rename(columns={'Giá trị giao dịch': 'Volume'}, inplace=True)

    # st.write(df_candle_hh.columns)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    # Tạo biểu đồ nến Nhật từ dataframe df_candle_WTI
    candle_chart = mpl.plot(df_candle_hh, type='candle', style="yahoo", volume=True, figsize=(14, 6))
    # Hiển thị biểu đồ
    st.pyplot(candle_chart)

    # Tính các giá trị cao nhất, thấp nhất và trung bình của mức giá
    high_price = df_candle_hh['High'].max()
    low_price = df_candle_hh['Low'].min()
    average_price = df_candle_hh[['Open', 'Close', 'High', 'Low']].mean().mean()

    # Tính khối lượng giao dịch (volume) cao nhất và trung bình, chuyển đổi sang đơn vị tỷ đồng và làm tròn đến 2 chữ số thập phân
    max_volume = df_candle_hh['Volume'].max()
    average_volume = df_candle_hh['Volume'].mean()

    # Check if max_volume and average_volume are not NaN
    if not pd.isnull(max_volume):
        max_volume = round(max_volume, 2)
    if not pd.isnull(average_volume):
        average_volume = round(average_volume, 2)

    # Display the output in two columns
    col1, col2 = st.columns(2)

    with col1:
        st.write("Mức giá cao nhất:", round(high_price, 2))
        st.write("Mức giá thấp nhất:", round(low_price, 2))
        st.write("Mức giá trung bình trong một phiên:", round(average_price, 2))

    with col2:
        st.write("Giá trị giao dịch cao nhất:", max_volume, "tỷ đồng")
        st.write("Giá trị giao dịch trung bình trong một phiên:", average_volume, "tỷ đồng")



with st.expander("So sánh"):

    # Sắp xếp theo thời gian trong cột 'Ngày giờ thực hiện'
    df = df.sort_values(by='Ngày giờ thực hiện')

    # Groupby 'Ngày dữ liệu' và 'Hàng hóa', sau đó tính các giá trị mong muốn
    df_candle = df.groupby(['Ngày dữ liệu', 'Hàng hóa']).agg({
        'Giá khớp': ['first', 'last', 'max', 'min'],
        'KL giao dịch mua': ['sum'],
        'KL giao dịch bán': ['sum'],
        'Giá trị giao dịch': ['sum']
    }).reset_index()

    # Đặt lại tên cột
    df_candle.columns = ['Ngày dữ liệu', 'Hàng hóa', 'Open', 'Close', 'High', 'Low', 'KL giao dịch mua', 'KL giao dịch bán', 'Giá trị giao dịch']
    #df_candle_hh = df_candle[df_candle['Hàng hóa'] == 'Khí tự nhiên']


    # Groupby và tính tổng các cột 'KL giao dịch mua', 'KL giao dịch bán', 'Giá trị giao dịch'
    df_open_position = df.groupby(['Tên TKGD', "Nhóm KH", 'Ngày dữ liệu', 'Hàng hóa', 'Loại giao dịch']).agg({
        'KL giao dịch mua': 'sum',
        'KL giao dịch bán': 'sum',
        'Giá trị giao dịch': 'sum'
    }).reset_index()

    # Tạo các hàm để áp dụng vào từng dòng của dataframe
    def calculate_open_position_mua(row):
        if row['KL giao dịch mua'] > row['KL giao dịch bán']:
            return row['KL giao dịch mua'] - row['KL giao dịch bán']
        else:
            return 0

    def calculate_open_position_ban(row):
        if row['KL giao dịch mua'] < row['KL giao dịch bán']:
            return row['KL giao dịch bán'] - row['KL giao dịch mua']
        else:
            return 0

    # Áp dụng các hàm vào từng dòng của dataframe để tạo các cột mới
    df_open_position['Vị thế mở mua'] = df_open_position.apply(calculate_open_position_mua, axis=1)
    df_open_position['Vị thế mở bán'] = df_open_position.apply(calculate_open_position_ban, axis=1)
    df_open_position["Tổng vị thế mở"] = df_open_position["Vị thế mở mua"] + df_open_position["Vị thế mở bán"]

    # Hiển thị dataframe sau khi thêm các cột mới

    option = st.selectbox('Select:', ('Tổng', 'Vị thế mua', 'Vị thế bán'), index=0)

    if option == 'Tổng':

        # Groupby theo 'Ngày dữ liệu' và 'Hàng hóa', tính tổng 'Giá trị giao dịch' cho mỗi ngày và mỗi loại hàng hóa
        total_value_by_date_and_item = df_candle.groupby(['Ngày dữ liệu', 'Hàng hóa'])['Giá trị giao dịch'].sum().unstack()


        # Tạo figure
        fig_1 = go.Figure()

        # Thêm các line cho từng loại hàng hóa
        for column in total_value_by_date_and_item.columns:
            fig_1.add_trace(go.Scatter(x=total_value_by_date_and_item.index, y=total_value_by_date_and_item[column], mode='lines+markers', name=column, marker_symbol='circle', marker_size=8,
                                    hovertemplate='%{y:.2f} tỷ đồng<br>'))  # Format hover data làm tròn 2 chữ số sau dấu phẩy

        # Thiết lập layout
        fig_1.update_layout(title='Tổng Giá trị giao dịch',
                        xaxis_title='Ngày',
                        yaxis_title='Tổng Giá trị giao dịch (tỷ đồng)',
                        xaxis=dict(tickangle=-45),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="right", x=0.8),
                        hovermode='x unified',
                        font=dict(family="Arial, sans-serif", size=12),
                        plot_bgcolor='rgba(250, 250, 250, 1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=50, r=50, t=70, b=50),
                        showlegend=True,
                        width=1200, height=600)  # Điều chỉnh độ rộng của biểu đồ

        # Hiển thị biểu đồ trên Streamlit
        st.plotly_chart(fig_1)

        # Groupby và tính tổng vị thế mở mua cho mỗi ngày và mỗi loại hàng hóa
        df_open_position_grouped = df_open_position.groupby(['Ngày dữ liệu', 'Hàng hóa'])['Tổng vị thế mở'].sum().reset_index()

        # Tạo biểu đồ linegraph
        fig_1a = go.Figure()

        # Thêm các line cho từng loại hàng hóa
        for hh in df_open_position_grouped['Hàng hóa'].unique():
            df_hh = df_open_position_grouped[df_open_position_grouped['Hàng hóa'] == hh]
            fig_1a.add_trace(go.Scatter(x=df_hh['Ngày dữ liệu'], y=df_hh['Tổng vị thế mở'], mode='lines', name=hh))

        # Thiết lập layout
        fig_1a.update_layout(title='Tổng vị thế mở',
                        xaxis_title='Ngày dữ liệu',
                        yaxis_title='Hợp đồng/lot',
                        legend_title='Hàng hóa', legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="right", x = 0.8),
                        hovermode='x unified',
                        font=dict(family="Arial, sans-serif", size=12),
                        plot_bgcolor='rgba(250, 250, 250, 1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=50, r=50, t=70, b=50),
                        showlegend=True,
                        width=1200, height=600)

        # Hiển thị biểu đồ
        st.plotly_chart(fig_1a)

    #-------------------------------------------
    if option == 'Vị thế mua':
        # Groupby theo 'Ngày dữ liệu' và 'Hàng hóa', tính tổng 'Giá trị giao dịch' cho mỗi ngày và mỗi loại hàng hóa
        total_volume_buy_by_date_and_item= df_candle.groupby(['Ngày dữ liệu', 'Hàng hóa'])['KL giao dịch mua'].sum().unstack()


        # Tạo figure
        fig_2 = go.Figure()

        # Thêm các line cho từng loại hàng hóa
        for column in total_volume_buy_by_date_and_item.columns:
            fig_2.add_trace(go.Scatter(x=total_volume_buy_by_date_and_item.index, y=total_volume_buy_by_date_and_item[column], mode='lines+markers', name=column, marker_symbol='circle', marker_size=8,
                                    hovertemplate='%{y:.0f}<br>'))  # Format hover data làm tròn 2 chữ số sau dấu phẩy

        # Thiết lập layout
        fig_2.update_layout(title='Tổng khối lượng mua theo ngày và loại hàng hóa (Hợp đồng/lot)',
                        xaxis_title='Ngày',
                        yaxis_title='Hợp đồng/lot',
                        xaxis=dict(tickangle=-45),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="right", x=0.8),
                        hovermode='x unified',
                        font=dict(family="Arial, sans-serif", size=12),
                        plot_bgcolor='rgba(250, 250, 250, 1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=50, r=50, t=70, b=50),
                        showlegend=True,
                        width=1200, height=600)  # Điều chỉnh độ rộng của biểu đồ

        # Hiển thị biểu đồ trên Streamlit
        st.plotly_chart(fig_2)

        # Groupby và tính tổng vị thế mở mua cho mỗi ngày và mỗi loại hàng hóa
        df_open_position_grouped = df_open_position.groupby(['Ngày dữ liệu', 'Hàng hóa'])['Vị thế mở mua'].sum().reset_index()

        # Tạo biểu đồ linegraph
        fig_2a = go.Figure()

        # Thêm các line cho từng loại hàng hóa
        for hh in df_open_position_grouped['Hàng hóa'].unique():
            df_hh = df_open_position_grouped[df_open_position_grouped['Hàng hóa'] == hh]
            fig_2a.add_trace(go.Scatter(x=df_hh['Ngày dữ liệu'], y=df_hh['Vị thế mở mua'], mode='lines', name=hh))

        # Thiết lập layout
        fig_2a.update_layout(title='Vị thế mở mua',
                        xaxis_title='Ngày dữ liệu',
                        yaxis_title='Hợp đồng/lot',
                        legend_title='Hàng hóa', legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="right", x = 0.8),
                        hovermode='x unified',
                        font=dict(family="Arial, sans-serif", size=12),
                        plot_bgcolor='rgba(250, 250, 250, 1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=50, r=50, t=70, b=50),
                        showlegend=True,
                        width=1200, height=600)

        # Hiển thị biểu đồ
        st.plotly_chart(fig_2a)


    #-------------------------------------------------------------------------------------

    if option == 'Vị thế bán':
        # Groupby theo 'Ngày dữ liệu' và 'Hàng hóa', tính tổng 'Giá trị giao dịch' cho mỗi ngày và mỗi loại hàng hóa
        total_volume_sell_by_date_and_item= df_candle.groupby(['Ngày dữ liệu', 'Hàng hóa'])['KL giao dịch bán'].sum().unstack()


        # Tạo figure
        fig_3 = go.Figure()

        # Thêm các line cho từng loại hàng hóa
        for column in total_volume_sell_by_date_and_item.columns:
            fig_3.add_trace(go.Scatter(x=total_volume_sell_by_date_and_item.index, y=total_volume_sell_by_date_and_item[column], mode='lines+markers', name=column, marker_symbol='circle', marker_size=8,
                                    hovertemplate='%{y:.0f}<br>'))  # Format hover data làm tròn 2 chữ số sau dấu phẩy

        # Thiết lập layout
        fig_3.update_layout(title='Tổng khối lượng mua theo ngày và loại hàng hóa (Hợp đồng/lot)',
                        xaxis_title='Ngày',
                        yaxis_title='Hợp đồng/lot',
                        xaxis=dict(tickangle=-45),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="right", x=0.8),
                        hovermode='x unified',
                        font=dict(family="Arial, sans-serif", size=12),
                        plot_bgcolor='rgba(250, 250, 250, 1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=50, r=50, t=70, b=50),
                        showlegend=True,
                        width=1200, height=600)  # Điều chỉnh độ rộng của biểu đồ

        # Hiển thị biểu đồ trên Streamlit
        st.plotly_chart(fig_3)

        #--------------------

        # Groupby và tính tổng vị thế mở mua cho mỗi ngày và mỗi loại hàng hóa
        df_open_position_grouped = df_open_position.groupby(['Ngày dữ liệu', 'Hàng hóa'])['Vị thế mở bán'].sum().reset_index()

        # Tạo biểu đồ linegraph
        fig_3a = go.Figure()

        # Thêm các line cho từng loại hàng hóa
        for hh in df_open_position_grouped['Hàng hóa'].unique():
            df_hh = df_open_position_grouped[df_open_position_grouped['Hàng hóa'] == hh]
            fig_3a.add_trace(go.Scatter(x=df_hh['Ngày dữ liệu'], y=df_hh['Vị thế mở bán'], mode='lines', name=hh))

        # Thiết lập layout
        fig_3a.update_layout(title='Tổng số vị thế mở bán',
                        xaxis_title='Ngày dữ liệu',
                        yaxis_title='Hợp đồng/lot',
                        legend_title='Hàng hóa', legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="right", x=0.8),
                        hovermode='x unified',
                        font=dict(family="Arial, sans-serif", size=12),
                        plot_bgcolor='rgba(250, 250, 250, 1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=50, r=50, t=70, b=50),
                        showlegend=True,
                        width=1200, height=600)

        # Hiển thị biểu đồ
        st.plotly_chart(fig_3a)
    
with st.expander("Tài khoản giao dịch"):
    # Groupby theo 'Nhóm KH' và tính tổng 'Giá trị giao dịch' cho mỗi nhóm
    df_pie= df_open_position.groupby('Nhóm KH')['Giá trị giao dịch'].sum().reset_index()
    # Điều chỉnh DataFrame df_pie bằng cách tính tỷ trọng
    total_value = df_pie['Giá trị giao dịch'].sum()
    df_pie['Tỷ trọng (%)'] = (df_pie['Giá trị giao dịch'] / total_value * 100).round(1)

    # Vẽ biểu đồ tròn
    fig_pie = px.pie(df_pie, values='Giá trị giao dịch', names='Nhóm KH', 
                title='Tỉ trọng giá trị giao dịch theo Nhóm KH',
                labels={'Giá trị giao dịch': 'Giá trị giao dịch (tỷ đồng)', 'Nhóm KH': 'Nhóm KH'}, width=550)

    # Hiển thị tỷ trọng của giá trị
    for i in range(len(df_pie)):
        fig_pie.add_annotation(x=df_pie.iloc[i]['Nhóm KH'], y=df_pie.iloc[i]['Giá trị giao dịch'],
                        text=f"{df_pie.iloc[i]['Tỷ trọng (%)']}%", showarrow=False)

    # Groupby theo 'Nhóm KH' và tính tổng 'Giá trị giao dịch' cho mỗi nhóm trong sản phẩm cụ thể
    df_open_position_hh = df_open_position[df_open_position["Hàng hóa"] == product]
    df_pie_hh = df_open_position_hh.groupby('Nhóm KH')['Giá trị giao dịch'].sum().reset_index()
    # Điều chỉnh DataFrame df_pie_hh bằng cách tính tỷ trọng
    total_value_hh = df_pie_hh['Giá trị giao dịch'].sum()
    df_pie_hh['Tỷ trọng (%)'] = (df_pie_hh['Giá trị giao dịch'] / total_value_hh * 100).round(1)

    # Vẽ biểu đồ tròn cho sản phẩm cụ thể
    fig_pie_hh = px.pie(df_pie_hh, values='Giá trị giao dịch', names='Nhóm KH', 
                title=f'Tỉ trọng giá trị giao dịch theo Nhóm KH của mặt hàng {product}',
                labels={'Giá trị giao dịch': 'Giá trị giao dịch (tỷ đồng)', 'Nhóm KH': 'Nhóm KH'}, width=550)

    # Hiển thị tỷ trọng của giá trị
    for i in range(len(df_pie_hh)):
        fig_pie_hh.add_annotation(x=df_pie_hh.iloc[i]['Nhóm KH'], y=df_pie_hh.iloc[i]['Giá trị giao dịch'],
                        text=f"{df_pie_hh.iloc[i]['Tỷ trọng (%)']}%", showarrow=False)

    # Hiển thị cả hai biểu đồ
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pie)
    with col2:
        st.plotly_chart(fig_pie_hh)

    df_open_position_pn = df_open_position[df_open_position['Nhóm KH'] == "Pháp nhân"]
    df_pn = df_open_position_pn.groupby('Tên TKGD')['Giá trị giao dịch'].sum().reset_index()
    df_pn = df_pn.sort_values(by='Giá trị giao dịch', ascending=True)


    # Tạo biểu đồ horizontal bar chart và thiết lập màu sắc
    fig_bar = go.Figure(go.Bar(
                x=df_pn['Giá trị giao dịch'],
                y=df_pn['Tên TKGD'],
                orientation='h',
                marker_color='#83C9FF'  # Màu của thanh biểu đồ
    ))

    # Thiết lập layout
    fig_bar.update_layout(title='Giá trị giao dịch tất cả các loại hàng hóa theo pháp nhân',
                    xaxis_title='tỷ đồng',
                    #yaxis_title='Tên TKGD',
                    font=dict(family="Arial, sans-serif", size=12),
                    plot_bgcolor='rgba(0, 00, 0, 0)',
                    paper_bgcolor='rgba(0, 00, 0, 0)',
                    margin=dict(l=250) #, r=50, t=70, b=50)
                    , width=550)
    
    df_open_position_pn_hh = df_open_position_hh[df_open_position_hh['Nhóm KH'] == "Pháp nhân"]
    df_pn_hh = df_open_position_pn_hh.groupby('Tên TKGD')['Giá trị giao dịch'].sum().reset_index()
    df_pn_hh = df_pn_hh.sort_values(by='Giá trị giao dịch', ascending=True)


    # Tạo biểu đồ horizontal bar chart và thiết lập màu sắc
    fig_bar_hh = go.Figure(go.Bar(
                x=df_pn_hh['Giá trị giao dịch'],
                y=df_pn_hh['Tên TKGD'],
                orientation='h',
                marker_color='#83C9FF'  # Màu của thanh biểu đồ
    ))

    # Thiết lập layout
    fig_bar_hh.update_layout(title=f'Giá trị giao dịch mặt hàng {product} theo pháp nhân',
                    xaxis_title='tỷ đồng',
                    #yaxis_title='Tên TKGD',
                    font=dict(family="Arial, sans-serif", size=12),
                    plot_bgcolor='rgba(0, 00, 0, 0)',
                    paper_bgcolor='rgba(0, 00, 0, 0)',
                    margin=dict(l=250) #, r=50, t=70, b=50)
                    , width=550)


    # Hiển thị cả hai biểu đồ
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_bar)
    with col2:
        st.plotly_chart(fig_bar_hh)
