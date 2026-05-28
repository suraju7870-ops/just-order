import streamlit as st
import sqlite3
import datetime
import os
import urllib.parse

# === 1. DATABASE SETUP ===
def init_db():
    conn = sqlite3.connect("just_order_v6.db")
    cursor = conn.cursor()
    
    # Shops Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            shop_type TEXT NOT NULL, 
            status INTEGER DEFAULT 1,
            rating REAL DEFAULT 4.5,
            rating_count INTEGER DEFAULT 1
        )
    """)
    
    # Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER,
            item_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            item_image TEXT, 
            FOREIGN KEY(shop_id) REFERENCES shops(id)
        )
    """)
    
    # Orders Table (Added: shop_name, delivery_boy, order_status columns)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT,
            ordered_by TEXT NOT NULL,       
            deliver_to TEXT NOT NULL,       
            delivery_address TEXT NOT NULL, 
            total_amount INTEGER NOT NULL,
            service_type TEXT NOT NULL,     
            open_box_required INTEGER,     
            payment_status TEXT DEFAULT 'Pending',
            order_status TEXT DEFAULT 'Received 📦', -- 'Received', 'Preparing in Kitchen 🍳', 'Out for Delivery 🛵', 'Delivered ✅'
            delivery_boy TEXT DEFAULT 'Not Assigned ❌',
            order_time TEXT
        )
    """)
    
    # Dummy Data Setup
    cursor.execute("SELECT COUNT(*) FROM shops")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO shops (name, shop_type, status) VALUES ('Blue Knight Restaurant', 'Food', 1)")
        cursor.execute("INSERT INTO shops (name, shop_type, status) VALUES ('Kalyanpur Kirana Store', 'Grocery', 1)")
        cursor.execute("INSERT INTO items (shop_id, item_name, price) VALUES (1, 'Simple Pizza', 150)")
        cursor.execute("INSERT INTO items (shop_id, item_name, price) VALUES (2, 'Fortune Oil 1L', 175)")
        
    conn.commit()
    conn.close()
    if not os.path.exists("uploaded_images"):
        os.makedirs("uploaded_images")

init_db()

# === UTILITY: WHATSAPP FORMATTING ===
def generate_whatsapp_link(phone, name, items_summary, grand_total, address, status_msg):
    bill_text = f"🛵 *JUST ORDER LIVE STATUS* 🛵\n\n"
    bill_text += f"🆔 *Order Status:* {status_msg}\n"
    bill_text += f"👤 *Customer:* {name}\n"
    bill_text += f"📦 *Items:*\n{items_summary}\n"
    bill_text += f"💰 *Total Bill:* ₹{grand_total}\n"
    bill_text += f"📍 *Landmark Address:* {address}\n\n"
    bill_text += f"Aapka order process ho raha hai! Just Order Team."
    
    encoded_text = urllib.parse.quote(bill_text)
    if not phone.startswith('+') and not phone.startswith('91') and len(phone) == 10:
        phone = "91" + phone
    return f"https://wa.me/{phone}?text={encoded_text}"


# === Streamlit Setup ===
st.set_page_config(page_title="Just Order - Logistics Engine", page_icon="📍", layout="wide")

# 😎 SWAG LOGO COMPONENT
def render_swag_logo():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e24 0%, #0a0a0c 100%); padding: 18px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #28a745; display: inline-block;">
        <span style="font-family: sans-serif; font-size: 38px; font-weight: 900; color: #ffffff;">JUST</span>
        <span style="font-family: sans-serif; font-size: 38px; font-weight: 900; color: #28a745;">ORDER</span> <span style="font-size: 28px;">📍</span>
        <p style="color: #a0a0a5; margin: 3px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; font-weight: bold;">Hyperlocal Delivery & Dispatch Center</p>
    </div>
    """, unsafe_allow_html=True)

# === 2. SIDEBAR NAVIGATION ===
st.sidebar.title("🎮 Navigation Hub")
app_mode = st.sidebar.selectbox("Select Screen Profile:", ["🛒 Customer App", "🏪 Merchant & Delivery Control Dashboard"])

# ==========================================================
# 🏪 PROFILE 1: CENTRAL CONTROL DASHBOARD (Merchant + Rider Hub)
# ==========================================================
if app_mode == "🏪 Merchant & Delivery Control Dashboard":
    render_swag_logo()
    st.title("👨‍💼 Just Order Merchant & Dispatch Terminal")
    
    password = st.text_input("Enter Control Key Password:", type="password")
    if password == "suraj123":
        st.success("Welcome, Access Granted!")
        
        tab_merchant, tab_dispatch, tab_edit = st.tabs(["🍳 1. Merchant Screen (Dukandar View)", "🛵 2. Rider Dispatch Hub (Delivery Control)", "✏️ 3. Modify Menu Prices"])
        
        # TAB 1: DUKANDAR PANEL
        with tab_merchant:
            st.subheader("🔴 Incoming Orders for Kitchen/Shops")
            st.info("Dukandar bhai is screen ko open rakhein. Jaise hi naya order aaye, khana banana chalu karein!")
            
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT order_id, shop_name, ordered_by, total_amount, order_status, order_time FROM orders WHERE order_status='Received 📦' OR order_status='Preparing in Kitchen 🍳' ORDER BY order_id DESC")
            active_orders = cursor.fetchall()
            
            if active_orders:
                for o in active_orders:
                    o_id, s_name, o_by, amt, o_stat, o_time = o
                    with st.container(border=True):
                        st.write(f"### 🎫 Order #{o_id} for **{s_name}**")
                        st.write(f"🕒 *Received At:* {o_time} | 📦 *Current Status:* `{o_stat}`")
                        
                        # Status buttons for merchant
                        if o_stat == "Received 📦":
                            if st.button(f"👨‍🍳 Accept & Start Preparing #{o_id}", key=f"prep_{o_id}"):
                                cursor.execute("UPDATE orders SET order_status='Preparing in Kitchen 🍳' WHERE order_id=?", (o_id,))
                                conn.commit()
                                st.rerun()
                        elif o_stat == "Preparing in Kitchen 🍳":
                            if st.button(f"✅ Mark as Food Ready/Packed #{o_id}", key=f"ready_{o_id}"):
                                cursor.execute("UPDATE orders SET order_status='Food Packed! Waiting for Rider 🎒' WHERE order_id=?", (o_id,))
                                conn.commit()
                                st.rerun()
            else:
                st.write("🎉 Wah! Abhi koi pending orders nahi hain dukanon ke liye.")
            conn.close()
            
        # TAB 2: DISPATCH HUB (RIDER SYSTEM)
        with tab_dispatch:
            st.subheader("🛵 Rider Management & Landmark Router")
            st.write("Yahan se aap kisi bhi ladke ko delivery ke liye bhej sakte hain aur use bina map landmark address dikha sakte hain.")
            
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT order_id, shop_name, deliver_to, delivery_address, total_amount, order_status, delivery_boy FROM orders WHERE order_status != 'Delivered ✅'")
            dispatch_rows = cursor.fetchall()
            
            if dispatch_rows:
                for row in dispatch_rows:
                    o_id, s_name, d_to, addr, amt, o_stat, d_boy = row
                    with st.expander(f"📦 Order #{o_id} [{o_stat}] ➔ Merchant: {s_name}"):
                        st.write(f"👤 *Deliver To (Customer Name & Phone):* **{d_to}**")
                        
                        # 📍 LANDMARK ROUTING HIGHLIGHT
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 12px; border-left: 5px solid #ffc107; border-radius: 5px; margin: 10px 0;">
                            <strong>📍 Landmark Address (Bina Map ke Delivery Route):</strong><br>
                            <span style="font-size: 16px; color: #333;">{addr}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write(f"💰 *Collect Cash Amount:* **₹{amt}**")
                        st.write(f"🚴 *Assigned Rider:* `{d_boy}`")
                        
                        # Dropdown to assign rider
                        rider_choice = st.selectbox(f"Assign Delivery Boy for #{o_id}:", ["Amit Kumar (Bike)", "Ranjan Kumar (Cycle)", "Suraj Kumar (Rider)"], key=f"rider_sel_{o_id}")
                        if st.button(f"🚀 Send Rider on Duty #{o_id}"):
                            cursor.execute("UPDATE orders SET delivery_boy=?, order_status='Out for Delivery 🛵' WHERE order_id=?", (rider_choice, o_id))
                            conn.commit()
                            st.rerun()
                            
                        if o_stat == "Out for Delivery 🛵":
                            if st.button(f"🏁 Mark Order as Successfully Delivered #{o_id}", type="primary"):
                                cursor.execute("UPDATE orders SET order_status='Delivered ✅', payment_status='Paid' WHERE order_id=?", (o_id,))
                                conn.commit()
                                st.rerun()
            else:
                st.info("No active pending deliveries.")
            conn.close()

        # TAB 3: CHANGE PRICE
        with tab_edit:
            st.subheader("✏️ Change Item Name or Price Entry")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, item_name, price FROM items")
            items_list = cursor.fetchall()
            if items_list:
                item_map = {f"{i[1]} (₹{i[2]})": i[0] for i in items_list}
                selected_item = st.selectbox("Choose Product to Modify:", list(item_map.keys()))
                t_id = item_map[selected_item]
                
                cursor.execute("SELECT item_name, price FROM items WHERE id=?", (t_id,))
                curr_name, curr_price = cursor.fetchone()
                
                up_name = st.text_input("New Name:", value=curr_name)
                up_price = st.number_input("New Price (₹):", min_value=1, value=curr_price)
                if st.button("💾 Apply & Save Database Changes"):
                    cursor.execute("UPDATE items SET item_name=?, price=? WHERE id=?", (up_name, up_price, t_id))
                    conn.commit()
                    st.success("Successfully updated menu configuration!")
            conn.close()


# ==========================================================
# 🛒 PROFILE 2: THE MAIN CUSTOMER INTERFACE
# ==========================================================
else:
    render_swag_logo()
    st.write("### *Ek hi App se Sab Kuch Mangwayein!*")
    
    tab_food, tab_grocery = st.tabs(["🍔 Order Food (Zomato Style)", "🥦 Order Grocery & Veggies (Blinkit Style)"])
    
    # --- FOOD TAB ---
    with tab_food:
        st.header("Hot & Fresh Food Delivery Engine")
        conn = sqlite3.connect("just_order_v6.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status FROM shops WHERE shop_type='Food'")
        food_shops = cursor.fetchall()
        
        cart_food = {}
        selected_shop_name = ""
        if food_shops:
            food_options = {f[1]: (f[0], f[2]) for f in food_shops}
            selected_shop_name = st.selectbox("Choose Restaurant:", list(food_options.keys()))
            f_id, f_status = food_options[selected_shop_name]
            
            if f_status == 0:
                st.error("❌ Currently Closed!")
            else:
                st.success(f"Active Menu of {selected_shop_name}")
                cursor.execute("SELECT id, item_name, price, item_image FROM items WHERE shop_id=?", (f_id,))
                for item in cursor.fetchall():
                    i_id, i_name, i_price, i_img = item
                    st.image("https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&auto=format&fit=crop&q=60", width=160)
                    qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"f_{i_id}")
                    if qty > 0:
                        cart_food[i_name] = {"price": i_price, "qty": qty, "type": "Zomato Food", "shop": selected_shop_name}
        conn.close()

    # --- GROCERY TAB ---
    with tab_grocery:
        st.header("10-Minute Grocery Delivery Hub")
        conn = sqlite3.connect("just_order_v6.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status FROM shops WHERE shop_type='Grocery'")
        grocery_shops = cursor.fetchall()
        
        cart_grocery = {}
        if grocery_shops:
            g_options = {g[1]: (g[0], g[2]) for g in grocery_shops}
            selected_g_shop = st.selectbox("Choose Grocery Merchant:", list(g_options.keys()))
            g_id, g_status = g_options[selected_g_shop]
            
            if g_status == 0:
                st.error("❌ Currently Closed!")
            else:
                if not cart_food:  # If restaurant cart empty, override shop context
                    selected_shop_name = selected_g_shop
                cursor.execute("SELECT id, item_name, price, item_image FROM items WHERE shop_id=?", (g_id,))
                for item in cursor.fetchall():
                    i_id, i_name, i_price, i_img = item
                    st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&auto=format&fit=crop&q=60", width=160)
                    qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"g_{i_id}")
                    if qty > 0:
                        cart_grocery[i_name] = {"price": i_price, "qty": qty, "type": "Blinkit Grocery", "shop": selected_g_shop}
        conn.close()

    # --- BILL ENGINE ---
    final_cart = {**cart_food, **cart_grocery}
    if final_cart:
        st.markdown("---")
        st.subheader("🛍️ Checkout Summary")
        
        items_total = 0
        summary_txt = ""
        for name, info in final_cart.items():
            cost = info['price'] * info['qty']
            items_total += cost
            summary_txt += f"- {name} x {info['qty']}\n"
            st.write(f"• **{name}** x {info['qty']} = ₹{cost} ({info['type']})")
            
        delivery_fee = 30
        grand_total = items_total + delivery_fee
        st.write(f"📦 Items Total: ₹{items_total} | 🛵 Delivery Charge: ₹{delivery_fee}")
        st.write(f"### **Grand Total Bill: ₹{grand_total}**")
        
        st.markdown("---")
        person_a = st.text_input("Your Name & Phone Number:", placeholder="e.g. Suhani Kumari - 6204051301")
        address_landmark = st.text_area("Full Delivery Address & Clear Village Landmarks (e.g., Nearsarso oil meel):")
        pay_mode = st.radio("Choose Mode:", ["UPI Online Instant Pay", "Cash on Delivery (COD)"])
        
        if st.button("🏁 Place Final Just Order", type="primary"):
            if person_a and address_landmark:
                time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                p_status_db = "Paid via UPI" if pay_mode == "UPI Online Instant Pay" else "COD Pending"
                
                conn = sqlite3.connect("just_order_v6.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (shop_name, ordered_by, deliver_to, delivery_address, total_amount, service_type, open_box_required, payment_status, order_time)
                    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """, (selected_shop_name, person_a, person_a, address_landmark, grand_total, "Hybrid", p_status_db, time_now))
                conn.commit()
                conn.close()
                
                st.success("🎉 Awesome! Your order has been registered successfully.")
                st.balloons()
                
                # ONLINE AUTOMATIC WHATSAPP ROUTE
                if pay_mode == "UPI Online Instant Pay":
                    cust_phone = person_a.split("-")[-1].strip() if "-" in person_a else "0000000000"
                    wa_link = generate_whatsapp_link(cust_phone, person_a, summary_txt, grand_total, address_landmark, "Received & Paid Online 💳")
                    st.markdown(f'<a href="{wa_link}" target="_blank" style="background-color:#25D366; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block;">💬 Open WhatsApp & Confirm Order Link</a>', unsafe_allow_html=True)
            else:
                st.error("Please enter Name, Phone and Landmark details!")