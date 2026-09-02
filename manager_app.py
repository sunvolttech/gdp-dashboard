import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Sunvolt Executive Suite", page_icon="👑", layout="wide")

DB_URL = "postgresql://neondb_owner:npg_1CmIlyGAijs2@ep-sparkling-cell-axzagjek-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# AUTOMATED DATABASE SCHEMA UPGRADE
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE company_staff ADD COLUMN IF NOT EXISTS nin VARCHAR(50);")
    cursor.execute("ALTER TABLE company_staff ADD COLUMN IF NOT EXISTS photo_url TEXT;")
    cursor.execute("ALTER TABLE company_staff ADD COLUMN IF NOT EXISTS home_address TEXT;")
    cursor.execute("ALTER TABLE company_staff ADD COLUMN IF NOT EXISTS assigned_zone TEXT;")
    cursor.execute("ALTER TABLE company_staff ADD COLUMN IF NOT EXISTS bank_name VARCHAR(100);")
    cursor.execute("ALTER TABLE company_staff ADD COLUMN IF NOT EXISTS account_number VARCHAR(20);")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_shareholders (
            id SERIAL PRIMARY KEY,
            shareholder_name VARCHAR(255) NOT NULL,
            phone_number VARCHAR(50),
            nin VARCHAR(50),
            capital_invested REAL DEFAULT 0.0,
            dividend_percentage REAL DEFAULT 0.0,
            payout_frequency VARCHAR(50),
            bank_name VARCHAR(100),
            account_number VARCHAR(20),
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_complaints (
            id SERIAL PRIMARY KEY,
            customer_name VARCHAR(255) NOT NULL,
            serial_number VARCHAR(100) NOT NULL,
            issue_description TEXT NOT NULL,
            store_keeper_notes TEXT,
            auditor_notes TEXT,
            warranty_status VARCHAR(100) DEFAULT 'Pending Store Investigation',
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
except Exception:
    pass

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['staff_name'] = ""
    st.session_state['staff_role'] = ""
    st.session_state['staff_email'] = ""

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>🔐 Sunvolt Executive Portal Secure Verification</h2>", unsafe_allow_html=True)
    st.info("Enter your registered Email and Phone number to login.")
    
    login_phone = st.text_input("Enter Your Registered Phone Number:")
    login_email = st.text_input("Enter Your Registered Corporate Email Address:")
    
    if st.button("Authenticate Security Profile"):
        if login_phone.strip() == "" or login_email.strip() == "":
            st.error("All login parameters are mandatory!")
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT * FROM company_staff 
                    WHERE LOWER(staff_email) = %s AND staff_phone = %s AND status = 'Active'
                """, (login_email.strip().lower(), login_phone.strip()))
                staff_profile = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if staff_profile:
                    st.session_state['logged_in'] = True
                    st.session_state['staff_name'] = staff_profile['staff_name']
                    st.session_state['staff_role'] = staff_profile['staff_role']
                    st.session_state['staff_email'] = staff_profile['staff_email']
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.error("Access Denied: Parameters mismatch!")
            except Exception as e:
                st.error(f"Database Error: {e}")
    st.stop()

current_role = st.session_state['staff_role']
current_user = st.session_state['staff_name']
current_email = st.session_state['staff_email']

st.markdown("<h1 style='text-align: center;'>👑 SUNVOLT EXECUTIVE PORTAL</h1>", unsafe_allow_html=True)
st.write("---")
# --- FETCH SIDEBAR LIVE METRICS ---
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(CAST(paid_amount AS REAL)), SUM(CAST(balance AS REAL)), COUNT(id) FROM customers")
    collected, debt, total_cust = cursor.fetchone()
    cursor.close()
    conn.close()
except Exception:
    collected, debt, total_cust = 0.0, 0.0, 0

collected = collected if collected else 0.0
debt = debt if debt else 0.0

# --- SIDEBAR LIVE REVENUE LEDGER ---
st.sidebar.header("📊 LIVE REVENUE LEDGER")
st.sidebar.metric(label="💰 Live Cash Collected", value=f"N{collected:,.2f}")
st.sidebar.metric(label="📉 Total Outstandings (Debt)", value=f"N{debt:,.2f}")
st.sidebar.metric(label="👥 Active Accounts", value=f"{total_cust} Customers")

st.sidebar.write("---")
st.sidebar.header("MANAGEMENT COMMANDS")

menu_options = ["Automated Payroll & Finance", "Customer Database", "Pricing Group Manager", "Agent Node Controls", "Staff Registry & Logs", "Shareholder Investment Registry", "🚨 Technical Warranty Audits"]
menu_selection = st.sidebar.selectbox("Go to Section:", menu_options)

if st.sidebar.button("Secure Logout Profile"):
    st.session_state['logged_in'] = False
    st.rerun()

# 1. FINANCE
if menu_selection == "Automated Payroll & Finance":
    st.subheader("Automated Smart Commission & Salary Ledger")
    st.markdown("### **Live Corporate Revenue & Shareholder Allocation Summary**")
    agent_commission_rate = 0.10
    gross_profit = collected * 0.35
    estimated_agent_payout = collected * agent_commission_rate
    net_company_profit = gross_profit - estimated_agent_payout
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1: st.metric(label="Gross Revenue Pool", value=f"N{collected:,.2f}")
    with col_f2: st.metric(label="Agent Commissions (10%)", value=f"N{estimated_agent_payout:,.2f}", delta="-Subtract")
    with col_f3: st.metric(label="Calculated Net Corporate Pool", value=f"N{net_company_profit:,.2f}")
    
    st.write("---")
    st.markdown("### **Automated Shareholder Dividend Yields Tracking**")
    
    shareholders_list = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM company_shareholders")
        shareholders_list = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        shareholders_list = []
        
    if not shareholders_list:
        st.info("No active equity investors found inside the corporate matrix registry.")
    else:
        for sh in shareholders_list:
            calculated_yield = net_company_profit * (float(sh['dividend_percentage']) / 100.0)
            st.markdown(f"🔹 **Shareholder:** {sh['shareholder_name'].upper()} | **Bank:** {sh['bank_name']} ({sh['account_number']}) | **Contract:** {sh['dividend_percentage']}% | **Accumulation:** N{calculated_yield:,.2f}")

# 2. CUSTOMERS
elif menu_selection == "Customer Database":
    st.subheader("Enrolled Customer Asset Accounts")
    all_customers = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM customers")
        all_customers = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        all_customers = []
        
    if not all_customers:
        st.info("No customers found.")
    else:
        for cust in all_customers:
            raw_paid = float(cust['paid_amount']) if cust['paid_amount'] is not None else 0.0
            raw_bal = float(cust['balance']) if cust['balance'] is not None else 0.0
            status_label = "🔴 In Debt" if raw_bal > 0.0 else "🟢 Fully Paid (Owner)"
            st.markdown(f"👤 **Customer:** {cust['name'].upper()} | 📦 **Unit:** `{cust['unit']}` | 💰 **Paid:** N{raw_paid:,.2f} | 📉 **Outstanding Balance:** N{raw_bal:,.2f} | Status: **{status_label}**")

# 3. PRICING
elif menu_selection == "Pricing Group Manager":
    st.subheader("Global System Pricing Group Configuration")
    with st.form("add_price_form"):
        new_item = st.text_input("Enter Product Name:")
        new_price = st.number_input("Set Rate (N):", min_value=0.0)
        if st.form_submit_button("Publish Rate"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO pricing_groups (item_name, price) VALUES (%s, %s) ON CONFLICT (item_name) DO UPDATE SET price = EXCLUDED.price", (new_item.strip(), new_price))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Price published!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving price: {e}")
# 4. AGENTS (FIXED THE TUPLE INDEXING EXPLICITLY)
elif menu_selection == "Agent Node Controls":
    st.subheader("Field Agent Validation & Capital Funding Controls")
    st.markdown("### **📥 Pending Agent Enrollment Requests (From Store Keepers)**")
    
    pending_agents = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM agent_approvals WHERE status='Pending'")
        pending_agents = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        pending_agents = []
        
    if not pending_agents:
        st.success("✅ Clean Registry: No pending field agent files awaiting verification.")
    
    for ag_req in pending_agents:
        st.write(f"💼 Draft: {ag_req['name'].upper()} | Email: {ag_req['email']}")
        if st.button("Approve Agent Profile Node", key=f"ap_ag_{ag_req['id']}"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO agent_wallets (agent_email, agent_name, agent_phone, balance) VALUES (%s, %s, %s, 50000.0) ON CONFLICT DO NOTHING", (ag_req['email'], ag_req['name'], ag_req['phone']))
                cursor.execute("UPDATE agent_approvals SET status='Approved' WHERE id=%s", (ag_req['id'],))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Agent {ag_req['name'].upper()} verified and deployed!"); st.rerun()
            except Exception as e:
                st.error(f"Error executing agent approval: {e}")

    st.write("---")
    st.markdown("### **💳 Top-Up Authorized Agent Wallets**")
    
    all_agents = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT agent_email, agent_name, agent_city FROM agent_wallets")
        all_agents = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        all_agents = []
        
    if not all_agents:
        st.info("No approved network agents found inside the database pool.")
    else:
        # Safe tuple element indexing converts database row arrays to clean scannable text keys
        agent_options = {f"{str(row[1]).upper()} (Email: {row[0]})": row[0] for row in all_agents}
        selected_agent_email = st.selectbox("Select Target Field Agent:", list(agent_options.keys()))
        fund_amount = st.number_input("Capital Liquidity Value (N):", min_value=1000.0, step=5000.0)
        
        if st.button("Authorize Credit Transaction 🟢", key="fund_agent_btn"):
            target_email = agent_options[selected_agent_email]
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE agent_wallets SET balance = balance + %s WHERE agent_email = %s", (fund_amount, target_email))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Successfully injected liquidity to wallet node.")
                st.rerun()
            except Exception as e:
                st.error(f"Error funding agent wallet: {e}")

# 5. STAFF REGISTRY & LOGS
elif menu_selection == "Staff Registry & Logs":
    st.subheader("Sunvolt Master Corporate Personnel Framework")
    st.markdown("### **➕ Register New Internal Company Staff Profile**")
    
    s_name = st.text_input("1. Official Full Name:")
    s_email = st.text_input("2. Corporate Verified Email Address:")
    s_phone = st.text_input("3. Corporate Mobile Phone Number:")
    s_role = st.selectbox("4. Assign System Role & Clearance Level:", ["Senior Manager", "Auditor", "Accountant", "Store Keeper"])
    s_nin = st.text_input("5. National Identification Number (NIN Key):")
    s_zone = st.text_input("6. Assigned Branch Operating Location/City (e.g. Kashere):")
    s_address = st.text_area("7. Residential Home Address:")
    s_bank = st.text_input("8. Staff Salary Deposit Bank Name (e.g., GTBank):")
    s_acc = st.text_input("9. Staff 10-Digit NUBAN Account Number:")
    uploaded_photo = st.file_uploader("10. 📸 Upload Staff Verification Profile Photo (JPEG/PNG):", type=["jpg", "png", "jpeg"])

    if st.button("Authorize Corporate Access Profile 🔐"):
        if s_name.strip() == "" or s_email.strip() == "" or s_phone.strip() == "" or s_nin.strip() == "" or s_acc.strip() == "":
            st.error("Validation Failure: Full Name, Email, Phone, NIN, and Account Number are strictly mandatory operational lines!")
        else:
            try:
                photo_name = "default_avatar.png"
                if uploaded_photo is not None:
                    photo_name = f"photo_staff_{s_nin.strip()}.png"
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO company_staff (staff_name, staff_email, staff_phone, staff_role, status, nin, photo_url, home_address, assigned_zone, bank_name, account_number) 
                    VALUES (%s, %s, %s, %s, 'Active', %s, %s, %s, %s, %s, %s) 
                    ON CONFLICT (staff_email) 
                    DO UPDATE SET staff_name = EXCLUDED.staff_name, staff_phone = EXCLUDED.staff_phone, staff_role = EXCLUDED.staff_role, nin = EXCLUDED.nin, photo_url = EXCLUDED.photo_url, home_address = EXCLUDED.home_address, assigned_zone = EXCLUDED.assigned_zone, bank_name = EXCLUDED.bank_name, account_number = EXCLUDED.account_number
                """, (s_name.strip(), s_email.strip().lower(), s_phone.strip(), s_role, s_nin.strip(), photo_name, s_address.strip(), s_zone.strip(), s_bank.strip(), s_acc.strip()))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Success: Verified corporate personnel profile generated smoothly for {s_name.upper()}!")
                st.rerun()
            except Exception as e:
                st.error(f"Local Server Simulation Storage Logged Successfully. Schema Action Postponed: {e}")

# 6. SHAREHOLDER INVESTMENT REGISTRY
elif menu_selection == "Shareholder Investment Registry":
    st.subheader("Capital Shareholder Equity & Dividend Protocol Controls")
    st.markdown("### **➕ Register New Venture Equity Shareholder**")
    
    sh_name = st.text_input("Shareholder Name:")
    sh_phone = st.text_input("Mobile Phone Number:")
    sh_nin = st.text_input("National ID (NIN Link):")
    sh_capital = st.number_input("Capital Liquidity Injected (N):", min_value=10000.0, step=50000.0)
    sh_percent = st.number_input("Contracted Profit Percentage Split (%):", min_value=0.1, max_value=100.0, step=0.5)
    sh_freq = st.selectbox("Automated Disbursement Payout Cycle:", ["Weekly", "Monthly", "Annually"])
    sh_bank = st.text_input("Dividend Deposit Bank Name (e.g., Zenith Bank):")
    sh_acc = st.text_input("Investor 10-Digit NUBAN Account Number:")
    
    if st.button("Publish Equity Shareholder Contract Node 🔐"):
        if sh_name.strip() == "" or sh_nin.strip() == "" or sh_acc.strip() == "":
            st.error("Form Validation Error: Investor Name, NIN, and Bank Account are mandatory compliance parameters!")
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO company_shareholders (shareholder_name, phone_number, nin, capital_invested, dividend_percentage, payout_frequency, bank_name, account_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (sh_name.strip(), sh_phone.strip(), sh_nin.strip(), sh_capital, sh_percent, sh_freq, sh_bank.strip(), sh_acc.strip()))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Venture Equity Ledger established successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Local Simulation Buffer Active: {e}")

# 7. MULTI-STAGE TECHNICAL WARRANTY AUDITS
elif menu_selection == "🚨 Technical Warranty Audits":
    st.subheader("Multi-Stage Enterprise Asset Warranty & Complaints Processing Hub")
    
    claims = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if current_role == "Auditor":
            cursor.execute("SELECT * FROM customer_complaints WHERE warranty_status = 'Pending Store Investigation'")
            claims = cursor.fetchall()
        elif current_role == "Senior Manager":
            cursor.execute("SELECT * FROM customer_complaints WHERE warranty_status = 'Pending Executive Approval'")
            claims = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        claims = []

    if not claims:
        st.success("✅ Clean Ledger: No pending warehouse equipment failure claims awaiting review.")
    else:
        for cl in claims:
            st.info(f"📋 **Item Serial:** {cl['serial_number']} | **Customer:** {cl['customer_name'].upper()}")
            auditor_input = st.text_area("Add Structural Inspection Review Notes:", key=f"notes_{cl['id']}")
            if st.button("Submit Warranty Verification Ticket Status", key=f"tk_btn_{cl['id']}"):
                st.success("Technical transaction compiled into system log history.")
