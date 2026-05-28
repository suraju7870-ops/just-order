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
            shop_phone TEXT DEFAULT '910000000000',
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
    
    # Orders Table
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
            order_status TEXT DEFAULT 'Received 📦', 
            delivery_boy TEXT DEFAULT 'Not Assigned ❌',
            order_time TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM shops")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO shops (name, shop_type, shop_phone, status) VALUES ('Blue Knight Restaurant', 'Food', '916204051301', 1)")
        cursor.execute("INSERT INTO shops (name, shop_type, shop_phone, status) VALUES ('Kalyanpur Kirana Store', 'Grocery', '916204051301', 1)")
        cursor.execute("INSERT INTO items (shop_id, item_name, price) VALUES (1, 'Simple Pizza', 150)")
        cursor.execute("INSERT INTO items (shop_id, item_name, price) VALUES (2, 'Fortune Oil 1L', 175)")
        
    conn.commit()
    conn.close()

init_db()

# === UTILITY: WHATSAPP MESSAGES ===
def generate_merchant_whatsapp_link(merchant_phone, shop_name, customer_name, customer_phone, items_summary, address_landmark):
    msg_text = f"🚨 *JUST ORDER - NEW ORDER RECEIVED* 🚨\n\n"
    msg_text += f"🏪 *Shop:* {shop_name}\n"
    msg_text += f"--------------------------------\n"
    msg_text += f"📦 *Order Items & Qty:*\n{items_summary}\n"
    msg_text += f"--------------------------------\n"
    msg_text += f"👤 *Customer:* {customer_name}\n"
    msg_text += f"📞 *Customer Call:* tel:{customer_phone}\n"
    msg_text += f"📍 *Delivery Landmark:* {address_landmark}\n\n"
    msg_text += f"Dukanadar bhai, kripya jaldi se order pack kijiye! 🍳🎒"
    return f"https://wa.me/{merchant_phone}?text={urllib.parse.quote(msg_text)}"

def generate_user_whatsapp_link(phone, name, items_summary, grand_total, address, status_msg):
    bill_text = f"🛵 *JUST ORDER LIVE STATUS* 🛵\n\n🆔 *Status:* {status_msg}\n👤 *Customer:* {name}\n📦 *Items:*\n{items_summary}\n💰 *Total:* ₹{grand_total}\n📍 *Address:* {address}"
    if not phone.startswith('+') and not phone.startswith('91') and len(phone) == 10:
        phone = "91" + phone
    return f"https://wa.me/{phone}?text={urllib.parse.quote(bill_text)}"


# === Streamlit Config ===
st.set_page_config(page_title="Just Order - Viral Marketing", page_icon="📍", layout="wide")

# 😎 SWAG LOGO COMPONENT
def render_swag_logo():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e24 0%, #0a0a0c 100%); padding: 18px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid #28a745; display: inline-block;">
        <span style="font-family: sans-serif; font-size: 38px; font-weight: 900; color: #ffffff;">JUST</span>
        <span style="font-family: sans-serif; font-size: 38px; font-weight: 900; color: #28a745;">ORDER</span> <span style="font-size: 28px;">📍</span>
        <p style="color: #a0a0a5; margin: 3px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; font-weight: bold;">Hyperlocal Delivery & Dispatch Center</p>
    </div>
    """, unsafe_allow_html=True)

# 🌟 THE EXPLICIT NEW FEATURE: CUSTOM SWAG SOCIAL MEDIA SHARING COMPONENT
def render_social_share_buttons():
    # Aapka exact live link jo image_12.png me chal raha h
    app_url = "https://just-order-cg2hmpqhgebmvbdkjvgynh.streamlit.app/"
    share_text = "Ab market ka khana aur ghar ka rashan mangwao seedhe ghar baithe Just Order App se! Try karo abhi: "
    
    # Social Share Links Generation
    whatsapp_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_text + app_url)}"
    facebook_share = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(app_url)}"
    
    share_html = f"""
    <div style="margin-bottom: 25px; background-color: #f8f9fa; padding: 15px; border-radius: 10px; display: inline-block; box-shadow: 0px 2px 5px rgba(0,0,0,0.05);">
        <strong style="color: #333; font-family: sans-serif; font-size: 14px; margin-right: 15px; display: block; margin-bottom: 10px;">📢 Apne Doston aur Parivar ko Share Karein:</strong>
        <a href="{whatsapp_share}" target="_blank" style="background-color: #25D366; color: white; padding: 8px 16px; text-decoration: none; border-radius: 20px; font-weight: bold; font-family: sans-serif; font-size: 13px; margin-right: 8px; display: inline-block;">🟢 WhatsApp Share</a>
        <a href="{facebook_share}" target="_blank" style="background-color: #1877F2; color: white; padding: 8px 16px; text-decoration: none; border-radius: 20px; font-weight: bold; font-family: sans-serif; font-size: 13px; margin-right: 8px; display: inline-block;">🔵 Facebook Share</a>
        <button onclick="navigator.clipboard.writeText('{app_url}'); alert('App Link Copied! Ab aap ise Instagram Story ya Bio me paste kar sakte hain. 😎');" style="background-color: #E1306C; color: white; padding: 8px 16px; border: none; border-radius: 20px; font-weight: bold; font-family: sans-serif; font-size: 13px; cursor: pointer; display: inline-block;">🟣 Copy for Instagram</button>
    </div>
    """
    st.markdown(share_html, unsafe_allow_html=True)


# === SIDEBAR NAV ===
st.sidebar.title("🎮 Navigation Hub")
app_mode = st.sidebar.selectbox("Select Screen Profile:", ["🛒 Customer App", "🏪 Merchant & Delivery Control Dashboard"])


# ==========================================================
# 🏪 PROFILE 1: CONTROL DASHBOARD (Role-Based Control)
# ==========================================================
if app_mode == "🏪 Merchant & Delivery Control Dashboard":
    render_swag_logo()
    st.title("👨‍💼 Control & Management Console")
    password = st.text_input("Enter your Security Access Key Password:", type="password")
    
    if password == "shop123":
        st.success("🔒 Dukandar/Merchant Session Active!")
        st.subheader("🍳 Your Active Orders for Kitchen")
        
        conn = sqlite3.connect("just_order_v6.db")
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, shop_name, ordered_by, total_amount, order_status, order_time FROM orders WHERE order_status='Received 📦' OR order_status='Preparing in Kitchen 🍳' ORDER BY order_id DESC")
        active_orders = cursor.fetchall()
        
        if active_orders:
            for o in active_orders:
                o_id, s_name, o_by, amt, o_stat, o_time = o
                with st.container(border=True):
                    st.write(f"### 🎫 Order #{o_id} [{o_stat}]")
                    if o_stat == "Received 📦":
                        if st.button(f"👨‍🍳 Accept & Start Preparing #{o_id}", key=f"shop_prep_{o_id}"):
                            cursor.execute("UPDATE orders SET order_status='Preparing in Kitchen 🍳' WHERE order_id=?", (o_id,))
                            conn.commit()
                            st.rerun()
                    elif o_stat == "Preparing in Kitchen 🍳":
                        if st.button(f"✅ Mark as Packed / Ready #{o_id}", key=f"shop_ready_{o_id}"):
                            cursor.execute("UPDATE orders SET order_status='Food Packed! Waiting for Rider 🎒' WHERE order_id=?", (o_id,))
                            conn.commit()
                            st.rerun()
        else:
            st.write("🎉 No active kitchen orders right now!")
        conn.close()

    elif password == "suraj123":
        st.success("👑 Welcome back, Founder Suraj Kumar!")
        tab_dispatch, tab_add_merchant, tab_edit = st.tabs(["🛵 1. Rider Dispatch Hub", "➕ 2. Register Merchant Phone", "✏️ 3. Modify Menu Prices"])
        
        with tab_dispatch:
            st.subheader("🛵 Rider Management & Landmark Router")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT order_id, shop_name, deliver_to, delivery_address, total_amount, order_status, delivery_boy FROM orders WHERE order_status != 'Delivered ✅'")
            dispatch_rows = cursor.fetchall()
            if dispatch_rows:
                for row in dispatch_rows:
                    o_id, s_name, d_to, addr, amt, o_stat, d_boy = row
                    with st.expander(f"📦 Order #{o_id} [{o_stat}] ➔ Merchant: {s_name}"):
                        st.write(f"👤 *Customer:* **{d_to}**")
                        st.write(f"📍 *Landmark Address:* {addr}")
                        st.write(f"💰 *Collect Cash:* **₹{amt}**")
                        
                        rider_choice = st.selectbox(f"Assign Delivery Boy for #{o_id}:", ["Amit Kumar (Bike)", "Ranjan Kumar (Cycle)", "Suraj Kumar (Rider)"], key=f"adm_rider_{o_id}")
                        if st.button("🚀 Send Rider on Duty", key=f"btn_send_{o_id}"):
                            cursor.execute("UPDATE orders SET delivery_boy=?, order_status='Out for Delivery 🛵' WHERE order_id=?", (rider_choice, o_id))
                            conn.commit()
                            st.rerun()
                        if o_stat == "Out for Delivery 🛵":
                            if st.button("🏁 Mark Order as Successfully Delivered", type="primary", key=f"btn_deliv_{o_id}"):
                                cursor.execute("UPDATE orders SET order_status='Delivered ✅', payment_status='Paid' WHERE order_id=?", (o_id,))
                                conn.commit()
                                st.rerun()
            conn.close()

        with tab_add_merchant:
            st.subheader("➕ Add/Update Merchant WhatsApp Phone Numbers")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, shop_phone FROM shops")
            all_shops_list = cursor.fetchall()
            if all_shops_list:
                shop_map_phone = {f"{s[1]} (Current Phone: {s[2]})": s[0] for s in all_shops_list}
                selected_shop_ph = st.selectbox("Select Shop to update contact:", list(shop_map_phone.keys()))
                target_shop_id_ph = shop_map_phone[selected_shop_ph]
                new_phone_num = st.text_input("Enter Merchant WhatsApp Number (with 91):")
                if st.button("💾 Link Phone to Shop"):
                    if new_phone_num:
                        cursor.execute("UPDATE shops SET shop_phone=? WHERE id=?", (new_phone_num, target_shop_id_ph))
                        conn.commit()
                        st.success("Successfully Linked WhatsApp Channel!")
            conn.close()

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
                if st.button("💾 Apply Changes"):
                    cursor.execute("UPDATE items SET item_name=?, price=? WHERE id=?", (up_name, up_price, t_id))
                    conn.commit()
                    st.success("Successfully updated!")
            conn.close()


# ==========================================================
# 🛒 PROFILE 2: THE MAIN CUSTOMER INTERFACE (With Social Share)
# ==========================================================
else:
    render_swag_logo()
    
    # 🌟 NEW SOCIAL SHARE PANEL ADDED RIGHT HERE!
    render_social_share_buttons()
    
    st.write("### *Ek hi App se Sab Kuch Mangwayein!*")
    
    tab_food, tab_grocery = st.tabs(["🍔 Order Food", "🥦 Order Grocery & Veggies"])
    
    with tab_food:
        st.header("Hot & Fresh Food Delivery Engine")
        conn = sqlite3.connect("just_order_v6.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status, shop_phone FROM shops WHERE shop_type='Food'")
        food_shops = cursor.fetchall()
        
        cart_food = {}
        selected_shop_name = ""
        merchant_phone_db = ""
        if food_shops:
            food_options = {f[1]: (f[0], f[2], f[3]) for f in food_shops}
            selected_shop_name = st.selectbox("Choose Restaurant:", list(food_options.keys()))
            f_id, f_status, merchant_phone_db = food_options[selected_shop_name]
            
            if f_status == 0:
                st.error("❌ Currently Closed!")
            else:
                st.success(f"Active Menu of {selected_shop_name}")
                cursor.execute("SELECT id, item_name, price FROM items WHERE shop_id=?", (f_id,))
                for item in cursor.fetchall():
                    i_id, i_name, i_price = item
                    st.image("https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&auto=format&fit=crop&q=60", width=160)
                    qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"f_{i_id}")
                    if qty > 0:
                        cart_food[i_name] = {"price": i_price, "qty": qty, "type": "Zomato Food", "shop": selected_shop_name}
        conn.close()

    with tab_grocery:
        st.header("10-Minute Grocery Delivery Hub")
        conn = sqlite3.connect("just_order_v6.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status, shop_phone FROM shops WHERE shop_type='Grocery'")
        grocery_shops = cursor.fetchall()
        
        cart_grocery = {}
        if grocery_shops:
            g_options = {g[1]: (g[0], g[2], g[3]) for g in grocery_shops}
            selected_g_shop = st.selectbox("Choose Grocery Merchant:", list(g_options.keys()))
            g_id, g_status, g_phone = g_options[selected_g_shop]
            
            if g_status == 0:
                st.error("❌ Currently Closed!")
            else:
                if not cart_food:
                    selected_shop_name = selected_g_shop
                    merchant_phone_db = g_phone
                cursor.execute("SELECT id, item_name, price FROM items WHERE shop_id=?", (g_id,))
                for item in cursor.fetchall():
                    i_id, i_name, i_price = item
                    st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&auto=format&fit=crop&q=60", width=160)
                    qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"g_{i_id}")
                    if qty > 0:
                        cart_grocery[i_name] = {"price": i_price, "qty": qty, "type": "Blinkit Grocery", "shop": selected_g_shop}
        conn.close()

    final_cart = {**cart_food, **cart_grocery}
    if final_cart:
        st.markdown("---")
        st.subheader("🛍️ Checkout Summary")
        
        items_total = 0
        summary_txt = ""
        for name, info in final_cart.items():
            cost = info['price'] * info['qty']
            items_total += cost
            summary_txt += f"• {name} x {info['qty']} = ₹{cost}\n"
            st.write(f"• **{name}** x {info['qty']} = ₹{cost} ({info['type']})")
            
        delivery_fee = 30
        grand_total = items_total + delivery_fee
        st.write(f"📦 Items Total: ₹{items_total} | 🛵 Delivery Charge: ₹{delivery_fee}")
        st.write(f"### **Grand Total Bill: ₹{grand_total}**")
        
        st.markdown("---")
        person_a = st.text_input("Your Name & Phone Number:", placeholder="e.g. Suhani Kumari - 6204051301")
        address_landmark = st.text_area("Full Delivery Address & Clear Village Landmarks:")
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
                
                customer_only_phone = person_a.split("-")[-1].strip() if "-" in person_a else "0000000000"
                merchant_wa_link = generate_merchant_whatsapp_link(merchant_phone_db, selected_shop_name, person_a, customer_only_phone, summary_txt, address_landmark)
                
                st.markdown("### 🔔 Alert Dukandar Instantly")
                st.markdown(f'<a href="{merchant_wa_link}" target="_blank" style="background-color:#25D366; color:white; padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block; font-size:16px;">💬 Send Live Order Alert to {selected_shop_name}</a>', unsafe_allow_html=True)
            else:
                st.error("Please fill details!")