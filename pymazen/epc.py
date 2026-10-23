import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import Column, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# إعداد قاعدة البيانات
DATABASE_URL = "sqlite:///battery_company.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# جدول العملاء والحسابات
class Customer(Base):
  __tablename__ = "customers"
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False, unique=True)
  phone = Column(String, default="غير متوفر")
  balance = Column(Float, default=0.0)  # المبلغ الذي عليه


# جدول سجل الحركات
class Transaction(Base):
  __tablename__ = "transactions"
  id = Column(Integer, primary_key=True, autoincrement=True)
  customer_name = Column(String, nullable=False)
  trans_type = Column(String, nullable=False)  # "فاتورة مبيعات" أو "سند قبض"
  amount = Column(Float, nullable=False)
  date = Column(String, nullable=False)
  notes = Column(String)


Base.metadata.create_all(bind=engine)

# واجهة التطبيق
st.set_page_config(
    page_title="نظام إدارة شركة مشاريع الطاقة للبطاريات", page_icon="⚡", layout="wide"
)

st.title("⚡ نظام إدارة شركة مشاريع الطاقة للبطاريات )")
st.sidebar.header("📌 لوحة التحكم والعمليات")

menu = st.sidebar.selectbox(
    "اختر القائمة",
    [
        "إضافة فاتورة مبيعات",
        "إضافة سند قبض",
        "كشف حسابات العملاء اللحظي",
        "لوحة المدير (رفع ملف إكسل)",
    ],
)

session = SessionLocal()

if menu == "إضافة فاتورة مبيعات":
  st.subheader("📄 إصدار فاتورة مبيعات جديدة")
  col1, col2 = st.columns(2)
  with col1:
    customer_name = st.text_input("اسم العميل")
    phone_number = st.text_input("رقم الهاتف (لإرسال الرسالة الآلية)")
  with col2:
    amount = st.number_input("مبلغ الفاتورة ($)", min_value=0.0, step=10.0)
    notes = st.text_input("ملاحظات إضافية")

  if st.button("حفظ الفاتورة وإرسال الإشعار للعميل"):
    if customer_name and amount > 0:
      customer = (
          session.query(Customer).filter_by(name=customer_name).first()
      )
      if not customer:
        customer = Customer(
            name=customer_name, phone=phone_number, balance=0.0
        )
        session.add(customer)
        session.commit()
      else:
        if phone_number:
          customer.phone = phone_number

      # زيادة الدين على العميل
      customer.balance += amount

      current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
      new_trans = Transaction(
          customer_name=customer_name,
          trans_type="فاتورة مبيعات",
          amount=amount,
          date=current_time,
          notes=notes,
      )
      session.add(new_trans)
      session.commit()

      st.success(
          f"✅ تم حفظ الفاتورة وإضافة المبلغ. الإجمالي الجديد على العميل"
          f" ({customer_name}) هو: **{customer.balance:,.2f} دولار**"
      )
      st.info(
          f"📩 **تم إرسال إشعار للعميل ({customer.phone}):**\nعزيزنا العميل"
          f" {customer_name}، تم إضافة فاتورة جديدة بتاريخ {current_time} بمبلغ"
          f" {amount} $. المبلغ الإجمالي الجديد المتبقي عليك الآن:"
          f" **{customer.balance:,.2f} دولار**."
      )
    else:
      st.warning("الرجاء إدخال اسم العميل والمبلغ بشكل صحيح.")

elif menu == "إضافة سند قبض":
  st.subheader("💵 استلام دفعات نقدية (سند قبض)")
  col1, col2 = st.columns(2)
  with col1:
    customer_name = st.text_input("اسم العميل")
    phone_number = st.text_input("رقم الهاتف (لإرسال الإشعار)")
  with col2:
    amount = st.number_input("المبلغ المقبوض ($)", min_value=0.0, step=10.0)
    notes = st.text_input("ملاحظات (رقم السند / طريقة الدفع)")

  if st.button("حفظ سند القبض وتحديث الحساب"):
    if customer_name and amount > 0:
      customer = (
          session.query(Customer).filter_by(name=customer_name).first()
      )
      if not customer:
        customer = Customer(
            name=customer_name, phone=phone_number, balance=0.0
        )
        session.add(customer)
        session.commit()
      else:
        if phone_number:
          customer.phone = phone_number

      # تخفيض الدين عن العميل (سند قبض)
      customer.balance -= amount

      current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
      new_trans = Transaction(
          customer_name=customer_name,
          trans_type="سند قبض",
          amount=amount,
          date=current_time,
          notes=notes,
      )
      session.add(new_trans)
      session.commit()

      st.success(
          f"✅ تم حفظ سند القبض بنجاح! الرصيد الإجمالي الجديد على العميل"
          f" ({customer_name}) هو: **{customer.balance:,.2f} دولار**"
      )
      st.info(
          f"📩 **تم إرسال إشعار للعميل ({customer.phone}):**\nعزيزنا العميل"
          f" {customer_name}، تم استلام سند قبض بتاريخ {current_time} بمبلغ"
          f" {amount} $. المبلغ الإجمالي الجديد المتبقي عليك الآن:"
          f" **{customer.balance:,.2f} دولار**."
      )
    else:
      st.warning("الرجاء إدخال اسم العميل والمبلغ بشكل صحيح.")

elif menu == "كشف حسابات العملاء اللحظي":
  st.subheader("📊 كشف حسابات العملاء المحدث (مزامنة فورية)")
  customers = session.query(Customer).all()
  if customers:
    for c in customers:
      with st.expander(
          f"👤 العميل: {c.name} | الهاتف: {c.phone} | المبلغ الحالي:"
          f" {c.balance:,.2f} $"
      ):
        st.write(f"**إجمالي المبلغ المتبقي عليه:** {c.balance:,.2f} دولار")
        st.write("📜 **سجل الحركات السابقة:**")
        trans_history = (
            session.query(Transaction)
            .filter_by(customer_name=c.name)
            .all()
        )
        if trans_history:
          for t in trans_history:
            st.markdown(
                f"- `{t.date}` | **{t.trans_type}**: `{t.amount} $` | ملاحظات:"
                f" {t.notes}"
            )
        else:
          st.write("لا توجد حركات مسجلة بعد لهذا العميل.")
  else:
    st.info("لا توجد حسابات عملاء مسجلة حالياً. يمكنك إضافتها عبر لوحة المدير.")

elif menu == "لوحة المدير (رفع ملف إكسل)":
  st.subheader("🔐 لوحة تحكم المدير - استيراد بيانات العملاء")
  pass_input = st.text_input("أدخل رمز مرور المدير:", type="password")

  if pass_input == "mmaa112000":
    st.success("تم تسجيل الدخول بنجاح كمدير للنظام!")
    st.write(
        "يرجى رفع ملف إكسل (Excel) يحتوي على الأعمدة التالية:"
        " **Customer_Name** (أو اسم العميل) و **Balance** (المبلغ الذي عليه)."
    )

    uploaded_file = st.file_uploader(
        "اختر ملف Excel للعملاء", type=["xlsx", "xls"]
    )
    if uploaded_file is not None:
      df = pd.read_excel(uploaded_file)
      st.write("معاينة البيانات المستخرجة من الملف:", df.head())

      if st.button("اعتماد وتخزين البيانات في النظام"):
        try:
          for index, row in df.iterrows():
            # يفترض أن الأعمدة في الإكسل تحتوي على اسم العميل والمبلغ
            c_name = str(row.iloc[1])  # العمود الثاني غالباً اسم العميل
            c_balance = float(row.iloc[2])  # العمود الثالث المبلغ

            existing_c = (
                session.query(Customer).filter_by(name=c_name).first()
            )
            if existing_c:
              existing_c.balance = c_balance
            else:
              new_c = Customer(
                  name=c_name, phone="غير متوفر", balance=c_balance
              )
              session.add(new_c)
          session.commit()
          st.success("تم استيراد وحفظ بيانات العملاء الافتراضية بنجاح!")
        except Exception as e:
          st.error(
              f"حدث خطأ أثناء قراءة الملف، تأكد من ترتيب الأعمدة: {e}"
          )
  elif pass_input != "":
    st.error("رمز المرور غير صحيح! يرجى التحقق.")

session.close()