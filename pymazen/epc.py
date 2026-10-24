import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import urllib.parse

st.set_page_config(
    page_title="نظام إدارة شركة مشاريع الطاقة للبطاريات",
    page_icon="⚡",
    layout="wide"
)

def init_db():
    conn = sqlite3.connect('battery_company.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            serial_no INTEGER UNIQUE,
            name TEXT NOT NULL,
            phone TEXT,
            balance INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trans_date TEXT NOT NULL,
            rep_name TEXT NOT NULL,
            customer_serial INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            trans_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            details TEXT
        )
    ''')
    
    c.execute("SELECT COUNT(*) FROM customers")
    if c.fetchone()[0] == 0:
        initial_data = [
            (2, "احمد زيد العبسي اب", "777000000", 170870),
            (1001, "عرفات الصياد للبطاريات", "777447172", 51796),
            (1003, "فخر الدين شوباص", "", 37872),
            (1006, "بسام المليكي القدسي", "", 126),
            (1007, "محلات ركن التوفير", "", 1348),
            (1010, "محمد صالح الكينعي صنعاء", "", 592),
            (1011, "الجرمي صنعاء عبد السلام قحطان", "", 35),
            (1014, "مازن حسين ناجي مودي", "", 4558),
            (1015, "ملقي", "", 1),
            (1016, "شركة القديمي للتجاره", "", 805),
            (1019, "محلات الدباء التجاريه", "", 74826),
            (1020, "ياسر محمد شوباص", "", 5969),
            (1022, "بشير عبد الله احمد عبادي", "", 1298),
            (1025, "بشير الجابري", "", 17131),
            (1026, "محمد محمد صالح الجابري", "", 3747),
            (1029, "محلات المليكي", "", 716),
            (1030, "الاشول للبطاريات", "", 0),
            (1031, "معين الشاطر", "", 158),
            (1032, "محلات المطري يحيى علي", "", 5912),
            (1034, "محلات وسيم محمد علي الصياد", "", 837),
            (1035, "عبد الجبار عتيق الصياد", "", 1309),
            (1785, "عمر محمد علي العثماني", "", 5010),
            (1786, "عبد الجليل احمد علي العامري", "", 460),
            (1787, "الاعلامي محمد الشيشان", "777114407", 714),
            (1789, "فتحي عبد الله اسحاق", "", 0),
            (1790, "عبد الكريم احمد عبد الله المجاهد", "777096650", 9610),
            (1791, "جبران يحيى صالح معلوم", "773505778", 20),
            (1792, "تقي الاعوج صنعاء", "771748443", 3048),
            (1793, "مجمع البركه احمد عبد الله", "735508242", 5),
            (1794, "محمد فتح عباس الوصابي", "777685799", 0),
            (1795, "قائد التويتي", "774535105", 400),
            (1796, "محلات الصلوي سامي عبد الوارق", "773110126", 0),
            (1797, "حزام يحيى محمد ردمان", "", 2233),
            (1798, "محلات الجابري للبطاريات", "716650822", 75),
            (1799, "محلات وليد الحبي اخوان", "770677639", 0),
            (1800, "محلات حمزه الشريف الحديده", "771802602", 370),
            (1801, "محلات العالميه الحديده", "776229148", 0),
            (1802, "محلات بن زيد للكهرباء", "735508450", 0),
            (1803, "حساب عملاء مؤقت", "", 0),
            (1804, "مناجي هادي دير عبد ربه", "778073495", 0),
            (1805, "ملك الكهرباء بشار شعوب", "785550068", 106),
            (1806, "محلات ناجي الشعيبي", "776566152", 0),
            (1807, "محلات علي يحيى حسين معلوم", "777717391", 7117),
            (1808, "محلات الابداع الفني", "711622244", 240),
            (1809, "محلات حميد جرمل", "772816799", 0),
            (1810, "انس مصطفى طه القربي", "774776971", 1004),
            (1811, "علي احمد طالب مشطل", "779077795", 10),
            (1812, "عدنان ناصر محمد النهدي", "774057828", 0),
            (1813, "بسام سيف حميد عبده", "771213470", 0),
            (1814, "محلات الامين حميد محمد", "771217301", 1),
            (1815, "محلات توفيق محمد عمر", "736508350", 0),
            (1816, "محلات بن عاصي صعدة", "777725304", 60),
            (1817, "حمود محمد حمود الطثي", "783561110", 0),
            (1818, "مؤسسة العطر وسام العطر", "771030080", 1),
            (1819, "محلات قاسم علم حجه", "770340410", 2054),
            (1820, "محمد عبد الله علي عبد القوم", "776238410", 20),
            (1821, "محلات الامانه التلفزيون", "777745094", 56515),
            (1822, "الخضر صالح حسين اليزيدي", "773134675", 500),
            (1823, "عبود عليوه محمد حسين", "770922892", 0)
        ]
        c.executemany("INSERT INTO customers (serial_no, name, phone, balance) VALUES (?, ?, ?, ?)", initial_data)
        
    conn.commit()
    conn.close()

init_db()

def get_connection():
    return sqlite3.connect('battery_company.db')

st.sidebar.title("⚡ تسجيل دخول المندوب")
reps_list = ["مازن", "المدير هارون", "نبيل الجابري", "محمد", "سامي مختار", "إبراهيم", "حسين الحميقاني"]
current_rep = st.sidebar.selectbox("اختر اسم المندوب الحالي:", ["-- اختر المندوب --"] + reps_list)

if current_rep == "-- اختر المندوب --":
    st.warning("⚠️ يرجى اختيار اسم المندوب من القائمة الجانبية للبدء في استخدام النظام.")
    st.stop()

st.sidebar.success(f"المندوب الحالي: {current_rep}")

menu = st.sidebar.radio("القائمة الرئيسية:", [
    "📝 إصدار فاتورة / سند جديد",
    "🔍 الاستعلام وكشف حساب عميل",
    "➕ إضافة عميل جديد",
    "📊 لوحة تحكم المدير ومتابعة المبيعات"
])

if menu == "📝 إصدار فاتورة / سند جديد":
    st.header("📝 إصدار حركة مالية / فاتورة جديدة")
    
    conn = get_connection()
    customers_df = pd.read_sql_query("SELECT serial_no, name, phone, balance FROM customers ORDER BY serial_no", conn)
    conn.close()
    
    cust_options = [f"{row['serial_no']} - {row['name']}" for _, row in customers_df.iterrows()]
    selected_cust = st.selectbox("البحث عن العميل (بالاسم أو الرقم التسلسلي):", ["-- اختر العميل --"] + cust_options)
    
    if selected_cust != "-- اختر العميل --":
        serial_no = int(selected_cust.split(" - ")[0])
        cust_info = customers_df[customers_df['serial_no'] == serial_no].iloc[0]
        
        st.info(f"**العميل:** {cust_info['name']} | **الرقم التسلسلي:** {cust_info['serial_no']} | **الهاتف:** {cust_info['phone']} | **الرصيد الحالي:** {cust_info['balance']:,} ASR")
        
        col1, col2 = st.columns(2)
        with col1:
            trans_type = st.selectbox("نوع الحركة:", ["فاتورة مبيعات", "سند قبض", "سند صرف"])
            amount = st.number_input("المبلغ (بالريال السعودي ASR):", min_value=1, step=1, value=100)
        with col2:
            trans_date = st.date_input("تاريخ الحركة:", value=date.today())
            details = st.text_input("تفاصيل / ملاحظات الفاتورة:")
            
        if st.button("💾 حفظ وإرسال إشعار للعميل عبر الواتساب"):
            conn = get_connection()
            c = conn.cursor()
            
            new_balance = cust_info['balance']
            if trans_type == "فاتورة مبيعات":
                new_balance += int(amount)
            elif trans_type == "سند قبض":
                new_balance -= int(amount)
            elif trans_type == "سند صرف":
                new_balance += int(amount)
                
            c.execute('''
                INSERT INTO transactions (trans_date, rep_name, customer_serial, customer_name, trans_type, amount, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (str(trans_date), current_rep, serial_no, cust_info['name'], trans_type, int(amount), details))
            
            c.execute("UPDATE customers SET balance = ? WHERE serial_no = ?", (new_balance, serial_no))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ تم حفظ الحركة بنجاح بواسطة المندوب: {current_rep}. الرصيد الجديد للعميل: {new_balance:,} ASR")
            
            msg = f"عزيزي العميل ({cust_info['name']})،\n" \
                  f"تم تسجيل ({trans_type}) بقيمة: {int(amount):,} ASR\n" \
                  f"التاريخ: {trans_date}\n" \
                  f"التفاصيل: {details if details else 'لاشيء'}\n" \
                  f"إجمالي الرصيد الحالي عليكم: {new_balance:,} ASR\n" \
                  f"--- شركة مشاريع الطاقة للبطاريات ⚡"
            
            encoded_msg = urllib.parse.quote(msg)
            phone_clean = "".join(filter(str.isdigit, str(cust_info['phone'])))
            
            if phone_clean:
                whatsapp_url = f"https://wa.me/{phone_clean}?text={encoded_msg}"
                st.markdown(f"### 📲 اضغط على الزر أدناه لإرسال الإشعار للعميل عبر الواتساب فوراً:")
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display:inline-block;padding:12px 20px;background-color:#25D366;color:white;text-decoration:none;border-radius:5px;font-weight:bold;">🚀 إرسال الرسالة عبر الواتساب للعميل</a>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ رقم هاتف العميل غير مسجل أو غير صالح، يرجى تحديث رقم الهاتف لإرسال الإشعار.")

elif menu == "🔍 الاستعلام وكشف حساب عميل":
    st.header("🔍 الاستعلام وكشف حساب عميل")
    
    conn = get_connection()
    customers_df = pd.read_sql_query("SELECT serial_no, name, phone, balance FROM customers ORDER BY serial_no", conn)
    
    search_query = st.text_input("أدخل اسم العميل أو الرقم التسلسلي للبحث:")
    
    if search_query:
        filtered_df = customers_df[
            customers_df['name'].str.contains(search_query, case=False, na=False) |
            customers_df['serial_no'].astype(str).str.contains(search_query)
        ]
        
        if not filtered_df.empty:
            st.dataframe(filtered_df.rename(columns={'serial_no': 'الرقم التسلسلي', 'name': 'اسم العميل', 'phone': 'الهاتف', 'balance': 'الرصيد الحالي (ASR)'}), use_container_width=True)
            
            selected_serial = st.selectbox("اختر عميل لعرض كشف الحساب التفصيلي:", filtered_df['serial_no'].tolist())
            
            if selected_serial:
                cust_data = customers_df[customers_df['serial_no'] == selected_serial].iloc[0]
                st.subheader(f"📄 كشف حساب العميل: {cust_data['name']} (رقم تسلسلي: {cust_data['serial_no']})")
                st.metric("الرصيد الحالي", f"{cust_data['balance']:,} ASR")
                
                trans_df = pd.read_sql_query('''
                    SELECT trans_date AS 'التاريخ', rep_name AS 'المندوب', trans_type AS 'نوع الحركة', amount AS 'المبلغ (ASR)', details AS 'التفاصيل'
                    FROM transactions WHERE customer_serial = ? ORDER BY id DESC
                ''', conn, params=(int(selected_serial),))
                
                if not trans_df.empty:
                    st.table(trans_df)
                else:
                    st.info("لا توجد حركات تسوق أو سداد سابقة مسجلة لهذا العميل.")
        else:
            st.error("لم يتم العثور على أي عميل ينطبق عليه البحث.")
    else:
        st.dataframe(customers_df.rename(columns={'serial_no': 'الرقم التسلسلي', 'name': 'اسم العميل', 'phone': 'الهاتف', 'balance': 'الرصيد الحالي (ASR)'}), use_container_width=True)
    
    conn.close()

elif menu == "➕ إضافة عميل جديد":
    st.header("➕ إضافة عميل جديد لكشف الشركة")
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT MAX(serial_no) FROM customers")
    max_serial = c.fetchone()[0] or 1823
    next_serial = max_serial + 1
    conn.close()
    
    st.info(f"💡 الترقيم التسلسلي التلقائي للعميل الجديد هو: **{next_serial}**")
    
    new_cust_name = st.text_input("اسم العميل الجديد بالكامل:")
    new_cust_phone = st.text_input("رقم هاتف العميل (واتساب):")
    initial_balance = st.number_input("الرصيد الافتتاحي (إن وجد - بالريال السعودي ASR):", value=0, step=1)
    
    if st.button("➕ إضافة العميل فوراً"):
        if new_cust_name.strip() != "":
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute("INSERT INTO customers (serial_no, name, phone, balance) VALUES (?, ?, ?, ?)",
                          (next_serial, new_cust_name.strip(), new_cust_phone.strip(), int(initial_balance)))
                conn.commit()
                st.success(f"✅ تم إضافة العميل '{new_cust_name}' بنجاح بالرقم التسلسلي: {next_serial}")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الإضافة: {e}")
            finally:
                conn.close()
        else:
            st.error("يرجى إدخال اسم العميل بشكل صحيح.")

elif menu == "📊 لوحة تحكم المدير ومتابعة المبيعات":
    st.header("📊 لوحة تحكم المدير ومتابعة أداء الموزعين")
    
    conn = get_connection()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("من تاريخ:", value=date.today())
    with col2:
        end_date = st.date_input("إلى تاريخ:", value=date.today())
    with col3:
        rep_filter = st.selectbox("تصفية حسب المندوب:", ["الكل"] + reps_list)
        
    query = "SELECT trans_date AS 'التاريخ', rep_name AS 'المندوب', customer_serial AS 'الرقم التسلسلي', customer_name AS 'اسم العميل', trans_type AS 'نوع الحركة', amount AS 'المبلغ (ASR)', details AS 'التفاصيل' FROM transactions WHERE trans_date BETWEEN ? AND ?"
    params = [str(start_date), str(end_date)]
    
    if rep_filter != "الكل":
        query += " AND rep_name = ?"
        params.append(rep_filter)
        
    query += " ORDER BY id DESC"
    
    report_df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    st.subheader(f"📑 تقرير حركة المبيعات والتحصيل من {start_date} إلى {end_date}")
    
    if not report_df.empty:
        sales_total = report_df[report_df['نوع الحركة'] == 'فاتورة مبيعات']['المبلغ (ASR)'].sum()
        received_total = report_df[report_df['نوع الحركة'] == 'سند قبض']['المبلغ (ASR)'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي المبيعات", f"{sales_total:,} ASR")
        m2.metric("إجمالي التحصيل", f"{received_total:,} ASR")
        m3.metric("عدد الحركات", len(report_df))
        
        st.dataframe(report_df, use_container_width=True)
    else:
        st.warning("لا توجد أي حركات مالية مسجلة خلال هذه الفترة المحددة.")
