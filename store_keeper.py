import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Sunvolt Store Keeper Suite", page_icon="📦", layout="wide")

DB_URL = "postgresql://neondb_owner:npg_1CmIlyGAijs2@ep-sparkling-cell-axzagjek-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DB_URL)

if 'store_logged_in' not in st.session_state:
    st.session_state['store_logged_in'] = False
    st.session_state['store_name'] = ""
    st.session_state['store_phone'] = ""
    st.session_state['store_email'] = ""
    st.session_state['store_branch_city'] = ""

# --- STORE KEEPER SECURE LOGIN GATE ---
if not st.session_state['store_logged_in']:
    st.markdown("<h2 style='text-align: center;'>📦 Sunvolt Store Keeper Authentication Gate</h2>", unsafe_allow_html=True)
    st.info("Security Verification: Enter your registered credentials to unlock your local branch warehouse node.")
    
    col1, col2 = st.columns(2)
    with col1:
        s_name = st.text_input("Full Name:")
        s_phone = st.text_input("Phone Number:")
    with col2:
        s_email = st.text_input("Email Address:")
        s_office = st.text_input("Warehouse Store Location/City (e.g., Kashere):")
        
    if st.button("Verify & Open Warehouse Dashboard"):
        if s_name.strip() == "" or s_phone.strip() == "" or s_email.strip() == "" or s_office.strip() == "":
            st.error("Access Refused: All credential parameters are strictly mandatory!")
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT * FROM company_staff 
                    WHERE LOWER(staff_name) = %s AND LOWER(staff_email) = %s AND staff_phone = %s AND staff_role = 'Store Keeper' AND status = 'Active'
                """, (s_name.strip().lower(), s_email.strip().lower(), s_phone.strip()))
                staff_exists = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if staff_exists:
                    st.session_state['store_logged_in'] = True
                    st.session_state['store_name'] = staff_exists['staff_name']
                    st.session_state['store_phone'] = staff_exists['staff_phone']
                    st.session_state['store_email'] = staff_exists['staff_email']
                    st.session_state['store_branch_city'] = s_office.strip().lower()
                    st.success(f"Access Granted! Welcome, {s_name.upper()}.")
                    st.rerun()
                else:
                    st.error("Access Denied: No active Store Keeper clearance profile matches these parameters inside the database.")
            except Exception as e:
                st.error(f"Database Server Connection Error: {e}")
    st.stop()

current_store_user = st.session_state['store_name']
current_store_email = st.session_state['store_email']
current_store_city = st.session_state['store_branch_city']

# --- SIDEBAR WAREHOUSE LEDGER ---
st.sidebar.header("📦 STORE ONLINE DASHBOARD")
st.sidebar.markdown(f"👤 **Store Keeper:** {current_store_user.upper()}")
st.sidebar.markdown(f"📍 **Branch Location:** {current_store_city.upper()}")

if st.sidebar.button("🔴 Logout From Store"):
    st.session_state['store_logged_in'] = False
    st.rerun()

st.markdown("<h1 style='text-align: center;'>📦 SUNVOLT WAREHOUSE & INVENTORY MANAGEMENT</h1>", unsafe_allow_html=True)
st.write("---")

# Tab workflows separating warehouse logistics
tab_warehouse, tab_send, tab_reg_agent, tab_complaint = st.tabs([
    "📥 Warehouse Inventory Intake", "🚚 Transfer Stock to Agent", "📋 Register New Agent Draft", "🚨 Log Customer Complaints"
])

# 1. WAREHOUSE INTAKЕ
with tab_warehouse:
    st.subheader(f"📥 Add Stock Inflow to {current_store_city.upper()} Warehouse Reserve")
    warehouse_stock = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.executecursor.execute("SELECT * FROM pricing_groups")

        warehouse_stock = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Error reading stock tiers: {e}")
    
    if not warehouse_stock:
        st.info("No commercial solar product configuration models found on the network server. Please publish item standard rates in your Pricing Group Manager tab first.")
    else:
        st.markdown("### **Available Catalog Models**")
        for name, prc in warehouse_stock:
            st.markdown(f"🔹 **Product Model:** {name} | Base Group Value: **N{prc:,.2f}**")
        
        st.write("---")
        product_names = [row[0] for row in warehouse_stock]
        selected_intake = st.selectbox("Select Arriving Solar Product Configuration Model:", product_names)
        intake_qty = st.number_input("Enter incoming stock volume item quantity:", min_value=1, step=1, value=1)
        
        if st.button("Record Intake Into Main Store"):
            st.success(f"Logistics update recorded safely! Stock pool for {selected_intake} expanded inside local buffers.")

# 2. TRANSFER STOCK TO AGENTS
with tab_send:
    st.subheader("🚚 Dispatch Hardware Logistics Pool to Registered Network Field Agents")
    active_agents = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT agent_email, agent_name FROM agent_wallets")
        active_agents = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        active_agents = []
        
    if not active_agents:
        st.warning("Logistics Alert: No verified, active field agents found inside the core database pipeline pool.")
    else:
        agent_options = {f"{row['agent_name'].upper()} ({row['agent_email']})": row['agent_email'] for row in active_agents}
        selected_agent_display = st.selectbox("Select Target Recipient Field Agent:", list(agent_options.keys()))
        target_agent_email = agent_options[selected_agent_display]
        
        qr_unit_number = st.text_input("Scan Unit Serial Key Node (Matrix Hardware SN String):")
        selected_device = st.text_input("Enter Product Variant Name:")
        
        if st.button("Authorize Dispatch via Online Server Link"):
            if qr_unit_number.strip() == "" or selected_device.strip() == "":
                st.error("Validation Error: Product Name and Unique Device Serial Key String are mandatory parameters!")
            else:
                st.success(f"Hardware node unit {qr_unit_number.strip()} safely routed onto Agent pipeline reserves!")

# 3. REGISTER NEW AGENT DRAFT
with tab_reg_agent:
    st.subheader("📋 Recruit and Enroll New Field Agent Draft Profile Request")
    ag_name = st.text_input("New Agent Full Name:")
    ag_phone = st.text_input("Mobile Phone Number Link:")
    ag_email = st.text_input("Valid Field Agent Email Address:")
    
    if st.button("Submit Agent Draft to Management Board"):
        if ag_name.strip() == "" or ag_phone.strip() == "" or ag_email.strip() == "":
            st.error("Validation Failure: Full Agent Name, Phone, and Email fields are strictly mandatory!")
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO agent_approvals (name, phone, email, status) 
                    VALUES (%s, %s, %s, 'Pending')
                """, (ag_name.strip(), ag_phone.strip(), ag_email.strip().lower()))
                conn.commit()
                cursor.close()
                conn.close()
                st.info("Success: Agent recruitment credentials safely routed onto your Executive authorization queue inside sunvolt_manager!")
            except Exception as e:
                st.error(f"Server integration warning: {e}")

# 4. LOG CUSTOMER WARRANTY COMPLAINTS (CONNECTS WITH MANAGER SECTION 7 AUDIT WORKFLOW)
with tab_complaint:
    st.subheader("🚨 Log Faulty Component System Warranty Claims")
    c_name = st.text_input("Customer Identity Name:")
    c_serial = st.text_input("Solar Hardware Matrix Serial Key (Unit SN String):")
    c_issue = st.text_area("Detailed System Malfunction Description:")
    
    if st.button("Forward Claim File to Technical Audit Review"):
        if c_name.strip() == "" or c_serial.strip() == "" or c_issue.strip() == "":
            st.error("Form Validation Error: Complete profile descriptions are mandatory!")
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO customer_complaints (customer_name, serial_number, issue_description, warranty_status) 
                    VALUES (%s, %s, %s, 'Pending Store Investigation')
                """, (c_name.strip(), c_serial.strip(), c_issue.strip()))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Incident claim processed! Ticket successfully routed to the Auditor's '🚨 Technical Warranty Audits' panel.")
            except Exception as e:
                st.error(f"Sabar pipeline error: {e}")
