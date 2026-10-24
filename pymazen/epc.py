import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
from supabase import create_client, Client

st.set_page_config(
    page_title="نظام إدارة شركة مشاريع الطاقة للبطاريات",
    page_icon="⚡",
    layout="wide"
)

# تصميم عصري وألوان احترافية متناسقة
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    .stButton>button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 12px 24px;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        color: white;
    }
    h1, h2, h3 {
        color: #f59e0b !important;
    }
    </style>
""", unsafe_allow_html=True)

# إعدادات الاتصال السحابي الرسمي بـ Supabase
SUPABASE_URL = "https://whqqmwpjwjgweuvssskd.supabase.co"
SUPABASE_KEY = "sb_publishable_mYn0TY-Vv0O3bnUE0DFoKA_MdTApPnV"

@st.cache_resource
def init_supabase() -> Client:
    if not SUPABASE_URL.startswith("https://"):
        st.error("❌ خطأ: رابط Supabase يجب أن يبدأ بـ https://")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# دالة جلب العملاء من السحابة
def get_customers():
    try:
        response = supabase.table("customers").select("*").order("serial_no").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["serial_no", "name", "phone", "balance"])
    except Exception as e:
        return pd.DataFrame(columns=["serial_no", "name", "phone", "balance"])

# دالة جلب الحركات من السحابة
def get_transactions():
    try:
        response = supabase.table("transactions").select("*").order("id", desc=True).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["trans_date", "rep_name", "customer_serial", "customer_name", "trans_type", "amount", "details"])
    except Exception as e:
        return pd.DataFrame(columns=["trans_date", "rep_name", "customer_serial", "customer_name", "trans_type", "amount", "details"])

# الشريط الجانبي لتسجيل دخول المندوب
st.sidebar.title("⚡ تسجيل دخول المندوب")
reps_list = ["المدير هارون", "حسين الحميقاني", "م / مازن القحفة", "سامي مختار", "نبيل الجابري", "إبراهيم", "محمد مختار"]
current_rep = st.sidebar.selectbox("اختر اسم المندوب الحالي:", ["-- اختر المندوب --"] + reps_list)

if current_rep == "-- اختر المندوب --":
    st.warning("⚠️ يرجى اختيار اسم المندوب من القائمة الجانبية للبدء.")
    st.stop()

st.sidebar.success(f"المندوب الحالي: {current_rep}")

menu = st.sidebar.radio("القائمة الرئيسية:", [
    "📝 إصدار فاتورة / سند جديد",
    "🔍 الاستعلام وكشف حساب عميل",
    "➕ إضافة عميل جديد",
    "📊 لوحة تحكم المدير ومتابعة المبيعات"
])

# 1. إصدار فاتورة / سند جديد
if menu == "📝 إصدار فاتورة / سند جديد":
    st.header("📝 إصدار حركة مالية وفاتورة جديدة (متزامن سحابياً)")
    
    customers_df = get_customers()
    
    if customers_df.empty:
        st.warning("⚠️ لا توجد بيانات عملاء حالياً في جدول `customers` بقاعدة البيانات.")
    else:
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
                
            if st.button("💾 حفظ وتحديث رصيد العميل سحابياً + إشعار الواتساب الإجباري"):
                new_balance = int(cust_info['balance'])
                if trans_type == "فاتورة مبيعات":
                    new_balance += int(amount)
                elif trans_type == "سند قبض":
                    new_balance -= int(amount)
                elif trans_type == "سند صرف":
                    new_balance += int(amount)
                    
                # إدخال الحركة في جدول transactions في Supabase
                supabase.table("transactions").insert({
                    "trans_date": str(trans_date),
                    "rep_name": current_rep,
                    "customer_serial": int(serial_no),
                    "customer_name": str(cust_info['name']),
                    "trans_type": str(trans_type),
                    "amount": int(amount),
                    "details": str(details)
                }).execute()
                
                # تحديث رصيد العميل في جدول customers في Supabase
                supabase.table("customers").update({"balance": new_balance}).eq("serial_no", int(serial_no)).execute()
                
                st.success(f"✅ تم الحفظ والتحديث السحابي بنجاح! الرصيد الجديد: {new_balance:,} ASR")
                
                msg = f"عزيزي العميل ({cust_info['name']})،\n" \
                      f"تم تسجيل ({trans_type}) بقيمة: {int(amount):,} ASR\n" \
                      f"التاريخ: {trans_date}\n" \
                      f"التفاصيل: {details if details else 'لا توجد'}\n" \
                      f"إجمالي الرصيد الحالي عليكم: {new_balance:,} ASR\n" \
                      f"--- شركة مشاريع الطاقة للبطاريات ⚡"
                
                st.markdown("### 📋 نص الإشعار والرسالة النصية الإجبارية للعميل:")
                st.code(msg, language="text")
                
                encoded_msg = urllib.parse.quote(msg)
                phone_clean = "".join(filter(str.isdigit, str(cust_info['phone'])))
                
                if phone_clean:
                    whatsapp_url = f"https://wa.me/{phone_clean}?text={encoded_msg}"
                    st.markdown(f'### 📲 <a href="{whatsapp_url}" target="_blank" style="padding:12px 20px;background-color:#25D366;color:white;text-decoration:none;border-radius:8px;font-weight:bold;display:inline-block;box-shadow: 0 4px 12px rgba(37,211,102,0.4);">🚀 إرسال الإشعار فوراً عبر الواتساب للعميل</a>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ رقم هاتف العميل غير مسجل، يمكنك نسخ النص أعلاه وإرساله للعميل مباشرة.")

# 2. الاستعلام وكشف حساب عميل
elif menu == "🔍 الاستعلام وكشف حساب عميل":
    st.header("🔍 الاستعلام وكشف حساب عميل (محدث لحظياً)")
    
    customers_df = get_customers()
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
                
                trans_response = supabase.table("transactions").select("*").eq("customer_serial", int(selected_serial)).order("id", desc=True).execute()
                trans_df = pd.DataFrame(trans_response.data) if trans_response.data else pd.DataFrame()
                
                if not trans_df.empty:
                    trans_df = trans_df.rename(columns={'trans_date': 'التاريخ', 'rep_name': 'المندوب', 'trans_type': 'نوع الحركة', 'amount': 'المبلغ (ASR)', 'details': 'التفاصيل'})
                    st.table(trans_df[['التاريخ', 'المندوب', 'نوع الحركة', 'المبلغ (ASR)', 'التفاصيل']])
                else:
                    st.info("لا توجد حركات سابقة مسجلة لهذا العميل.")
        else:
            st.error("لم يتم العثور على أي عميل بهذا الاسم أو الرقم.")
    else:
        st.dataframe(customers_df.rename(columns={'serial_no': 'الرقم التسلسلي', 'name': 'اسم العميل', 'phone': 'الهاتف', 'balance': 'الرصيد الحالي (ASR)'}), use_container_width=True)

# 3. إضافة عميل جديد
elif menu == "➕ إضافة عميل جديد":
    st.header("➕ إضافة عميل جديد وحفظه سحابياً ليظهر لدى الجميع فوراً")
    
    customers_df = get_customers()
    max_serial = int(customers_df['serial_no'].max()) if not customers_df.empty and 'serial_no' in customers_df.columns else 1823
    next_serial = max_serial + 1
    
    st.info(f"💡 الرقم التسلسلي التلقائي الممنوح للعميل الجديد: **{next_serial}**")
    
    new_cust_name = st.text_input("اسم العميل الجديد بالكامل:")
    new_cust_phone = st.text_input("رقم هاتف العميل (واتساب):")
    initial_balance = st.number_input("الرصيد الافتتاحي (بالريال السعودي ASR):", value=0, step=1)
    
    if st.button("➕ اعتماد وحفظ العميل في السحابة"):
        if new_cust_name.strip() != "":
            try:
                supabase.table("customers").insert({
                    "serial_no": int(next_serial),
                    "name": str(new_cust_name.strip()),
                    "phone": str(new_cust_phone.strip()),
                    "balance": int(initial_balance)
                }).execute()
                st.success(f"✅ تم حفظ العميل الجديد سحابياً بنجاح برقم تسلسلي: {next_serial} وسيراه جميع المندوبين فوراً!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ: {e}")
        else:
            st.error("يرجى إدخال اسم العميل بشكل صحيح.")

# 4. لوحة تحكم المدير
elif menu == "📊 لوحة تحكم المدير ومتابعة المبيعات":
    st.header("🔐 دخول لوحة تحكم المدير")
    password = st.text_input("أدخل كلمة مرور المدير للمتابعة:", type="password")
    
    if password == "772104060":
        st.success("🔓 تم التحقق من كلمة المرور بنجاح!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("من تاريخ:", value=date.today())
        with col2:
            end_date = st.date_input("إلى تاريخ:", value=date.today())
        with col3:
            rep_filter = st.selectbox("تصفية حسب المندوب:", ["الكل"] + reps_list)
            
        trans_df = get_transactions()
        
        if not trans_df.empty:
            trans_df['trans_date_parsed'] = pd.to_datetime(trans_df['trans_date']).dt.date
            filtered_report = trans_df[
                (trans_df['trans_date_parsed'] >= start_date) & 
                (trans_df['trans_date_parsed'] <= end_date)
            ]
            
            if rep_filter != "الكل":
                filtered_report = filtered_report[filtered_report['rep_name'] == rep_filter]
                
            st.subheader(f"📑 تقرير حركة المبيعات والتحصيل من {start_date} إلى {end_date}")
            
            if not filtered_report.empty:
                sales_total = filtered_report[filtered_report['trans_type'] == 'فاتورة مبيعات']['amount'].sum()
                received_total = filtered_report[filtered_report['trans_type'] == 'سند قبض']['amount'].sum()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("إجمالي المبيعات", f"{sales_total:,} ASR")
                m2.metric("إجمالي التحصيل", f"{received_total:,} ASR")
                m3.metric("عدد الحركات", len(filtered_report))
                
                display_report = filtered_report[['trans_date', 'rep_name', 'customer_serial', 'customer_name', 'trans_type', 'amount', 'details']].rename(columns={
                    'trans_date': 'التاريخ', 'rep_name': 'المندوب', 'customer_serial': 'الرقم التسلسلي', 
                    'customer_name': 'اسم العميل', 'trans_type': 'نوع الحركة', 'amount': 'المبلغ (ASR)', 'details': 'التفاصيل'
                })
                st.dataframe(display_report, use_container_width=True)
            else:
                st.warning("لا توجد أي حركات مالية مسجلة خلال هذه الفترة والشروط المحددة.")
        else:
            st.warning("لا توجد حركات مسجلة في النظام حتى الآن.")
            
    elif password != "":
        st.error("❌ كلمة المرور غير صحيحة!")
