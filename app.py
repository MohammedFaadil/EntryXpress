import streamlit as st
from utils.session import start_session, end_session, load_sessions, get_user_balance, add_balance, deduct_balance, register_user, user_exists
from utils.geofence import is_inside_mall
from utils.billing import calculate_charges
from datetime import datetime, timedelta
import geocoder
import pandas as pd
import qrcode
from io import BytesIO
import time

st.set_page_config(page_title="Mall Entry System", layout="wide")
st.image("assets/logo.png", width=300)
st.title("🛍️ Smart Mall Entry Ticketing System")

# ------------------------ Session Timeout ------------------------
if "last_interaction" in st.session_state and time.time() - st.session_state.last_interaction > 300:
    st.session_state.logged_in = False
    st.warning("⏱️ You were logged out due to inactivity.")
    st.stop()
st.session_state.last_interaction = time.time()

# ------------------------ Auth Section ------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title("🔐 Secure Account Access")
    auth_mode = st.sidebar.radio("Select Login Mode", ["Sign In", "Sign Up"])

    if auth_mode == "Sign In":
        login_email = st.sidebar.text_input("Enter Email or Phone")
        otp = st.sidebar.text_input("Enter OTP (simulated: 123456)", max_chars=6)
        login_button = st.sidebar.button("Sign In")

        if login_button:
            if login_email:
                if user_exists(login_email):
                    if otp == "123456":  # Simulated OTP
                        st.session_state.logged_in = True
                        st.session_state.user_id = login_email
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Invalid OTP. Try 123456 (demo).")
                else:
                    st.sidebar.error("⚠️ User not found. Please sign up.")
            else:
                st.sidebar.error("Email or Phone required.")

    elif auth_mode == "Sign Up":
        reg_name = st.sidebar.text_input("Full Name")
        reg_email = st.sidebar.text_input("Email")
        reg_phone = st.sidebar.text_input("Phone Number")
        reg_button = st.sidebar.button("Register")

        if reg_button:
            if reg_email or reg_phone:
                user_id = reg_email or reg_phone
                if not user_exists(user_id):
                    register_user(user_id, {"name": reg_name, "email": reg_email, "phone": reg_phone})
                    st.sidebar.success("🎉 Registered successfully! You can now Sign In.")
                else:
                    st.sidebar.error("⚠️ User already exists.")
            else:
                st.sidebar.error("Email or phone is required.")
    st.stop()

# ------------------------ Navigation ------------------------
menu = st.sidebar.selectbox("Navigation", ["Book Ticket", "Live Tracker", "Add Balance", "Admin Dashboard", "Logout"])

# ------------------------ Logout ------------------------
if menu == "Logout":
    st.session_state.logged_in = False
    st.success("👋 Logged out successfully.")
    st.stop()

# ------------------------ Book Ticket ------------------------
if menu == "Book Ticket":
    st.header("🎟️ Book Your Entry Ticket")
    with st.form("entry_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email", value=st.session_state.user_id)
        phone = st.text_input("Phone Number")
        submitted = st.form_submit_button("Book Ticket")

    if submitted:
        user_id = email or phone
        if not user_id:
            st.error("Email or phone is required.")
        else:
            user_data = {"name": name, "email": email, "phone": phone}
            start_session(user_id, user_data)
            st.success(f"🎟️ Ticket booked! Welcome {name} 👋")
            st.session_state["user_id"] = user_id

# ------------------------ Live Tracker ------------------------
elif menu == "Live Tracker":
    st.header("📍 Auto Track Location via GPS")
    user_id = st.session_state.user_id

    st.subheader("Checking Your Current Location...")
    g = geocoder.ip('me')
    if g.ok:
        lat, lon = g.latlng
        st.success(f"📍 Your Live Location: **Lat:** {lat:.6f}, **Lon:** {lon:.6f}")

        if is_inside_mall(lat, lon):
            st.success("✅ You are within Phoenix Mall Range.")
            st.info("🎟️ No ticket is needed.")
            st.map([{'lat': lat, 'lon': lon}])
        else:
            st.warning("🚧 You are outside the mall!")
            entry_time = end_session(user_id)
            if entry_time:
                charges = calculate_charges(entry_time)
                if charges == 0:
                    st.success("🕐 You stayed within 1 hour. No charges.")
                else:
                    success = deduct_balance(user_id, charges)
                    if success:
                        st.success(f"💸 ₹{charges} deducted from your balance.")
                    else:
                        st.error("❌ Insufficient balance. Please recharge!")
            else:
                st.error("❌ No active session found.")
    else:
        st.error("❌ Unable to fetch location. Check internet.")

# ------------------------ Add Balance ------------------------
elif menu == "Add Balance":
    st.header("💰 Recharge Your Account")
    user_id = st.session_state.user_id
    current_balance = get_user_balance(user_id)

    st.info(f"💵 Current balance: ₹{current_balance}")
    amount = st.number_input("Enter amount to add via UPI:", min_value=10, max_value=1000, step=10)

    if st.button("Generate UPI QR"):
        upi_url = f"upi://pay?pa=mall@upi&pn=MallEntrySystem&am={amount}&cu=INR"
        qr = qrcode.make(upi_url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf.getvalue(), caption="📱 Scan this QR to pay", use_column_width=False)

    if st.button("I have paid. Add Balance"):
        add_balance(user_id, amount)
        st.success(f"✅ ₹{amount} added successfully!")
        st.rerun()

# ------------------------ Admin Dashboard ------------------------
elif menu == "Admin Dashboard":
    st.header("🛠️ Admin Panel: Current Active Users")
    sessions = load_sessions()

    if sessions:
        data = []
        for user_id, session in sessions.items():
            entry_time = datetime.fromisoformat(session["entry_time"])
            duration = (datetime.now() - entry_time).total_seconds() / 60
            balance = get_user_balance(user_id)
            if balance < 50:
                st.warning(f"🔔 Low balance alert for {session['data']['name']} ({balance})")

            data.append({
                "Name": session["data"]["name"],
                "Phone": session["data"]["phone"],
                "Entry Time": entry_time.strftime("%Y-%m-%d %H:%M"),
                "Time Inside (mins)": round(duration, 2),
                "Balance (₹)": balance
            })

        df = pd.DataFrame(data)
        st.dataframe(df)

        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV Report", csv, "mall_entry_report.csv", "text/csv", key='download-csv')
    else:
        st.info("✅ No users currently inside the mall.")
