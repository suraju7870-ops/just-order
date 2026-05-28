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

# === UTILITY: WHATSAPP LINK FOR MERCHANT ===
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


# === Streamlit Page Design ===
st.set_page_config(page_title="Just Order - Smart Logistics", page_icon="📍", layout="wide")

def render_swag_logo():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1e24 0%, #0a0a0c 100%); padding: 18px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #28a745; display: inline-block;">
        <span style="font-family: sans-serif; font-size: 38px; font-weight: 900; color: #ffffff;">JUST</span>
        <span style="font-family: sans-serif; font-size: 38px; font-weight: 900; color: #28a745;">ORDER</span> <span style="font-size: 28px;">📍</span>
        <p style="color: #a0a0a5; margin: 3px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; font-weight: bold;">Hyperlocal Delivery & Dispatch Center</p>
    </div>
    """, unsafe_allow_html=True)

# === NAVIGATION ===
st.sidebar.title("🎮 Navigation Hub")
app_mode = st.sidebar.selectbox("Select Screen Profile:", ["🛒 Customer App", "🏪 Merchant & Delivery Control Dashboard"])


# ==========================================================
# 🏪 BACKEND CONTROL PROFILE
# ==========================================================
if app_mode == "🏪 Merchant & Delivery Control Dashboard":
    render_swag_logo()
    st.title("👨‍💼 Control & Management Console")
    password = st.text_input("Enter your Security Access Key Password:", type="password")
    
    if password == "shop123":
        st.success("🔒 Dukandar/Merchant Session Active!")
        conn = sqlite3.connect("just_order_v6.db")
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, shop_name, ordered_by, total_amount, order_status, order_time FROM orders WHERE order_status='Received 📦' OR order_status='Preparing in Kitchen 🍳' ORDER BY order_id DESC")
        active_orders = cursor.fetchall()
        if active_orders:
            for o in active_orders:
                o_id, s_name, o_by, amt, o_stat, o_time = o
                with st.container(border=True):
                    st.write(f"### 🎫 Order #{o_id} [{o_stat}]")
                    if o_stat == "Received 📦" and st.button(f"👨‍🍳 Accept #{o_id}", key=f"s_prep_{o_id}"):
                        cursor.execute("UPDATE orders SET order_status='Preparing in Kitchen 🍳' WHERE order_id=?", (o_id,))
                        conn.commit()
                        st.rerun()
                    elif o_stat == "Preparing in Kitchen 🍳" and st.button(f"✅ Ready #{o_id}", key=f"s_rd_{o_id}"):
                        cursor.execute("UPDATE orders SET order_status='Food Packed! Waiting for Rider 🎒' WHERE order_id=?", (o_id,))
                        conn.commit()
                        st.rerun()
        conn.close()

    elif password == "suraj123":
        st.success("👑 Welcome back, Founder Suraj Kumar!")
        tab_dispatch, tab_add_merchant, tab_edit = st.tabs(["🛵 1. Rider Dispatch Hub", "➕ 2. Register Merchant Phone", "✏️ 3. Modify Menu Prices"])
        
        with tab_dispatch:
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT order_id, shop_name, deliver_to, delivery_address, total_amount, order_status, delivery_boy FROM orders WHERE order_status != 'Delivered ✅'")
            for row in cursor.fetchall():
                o_id, s_name, d_to, addr, amt, o_stat, d_boy = row
                with st.expander(f"📦 Order #{o_id} ➔ {s_name}"):
                    st.write(f"📍 *Landmark Address:* {addr}")
                    rider_choice = st.selectbox("Rider:", ["Amit Kumar (Bike)", "Ranjan Kumar (Cycle)"], key=f"r_{o_id}")
                    if st.button("🚀 Dispatch", key=f"ds_{o_id}"):
                        cursor.execute("UPDATE orders SET delivery_boy=?, order_status='Out for Delivery 🛵' WHERE order_id=?", (rider_choice, o_id))
                        conn.commit()
                        st.rerun()
            conn.close()
            
        with tab_add_merchant:
            new_phone_num = st.text_input("Enter Merchant WhatsApp Number (e.g. 916204051301):")
            if st.button("💾 Link Phone"):
                st.success("Linked!")


# ==========================================================
# 🛒 FRONTEND CUSTOMER APP (With Integrated Swag Share Buttons)
# ==========================================================
else:
    render_swag_logo()
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
            if f_status != 0:
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
            if g_status != 0:
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
            st.write(f"• **{name}** x {info['qty']} = ₹{cost}")
            
        delivery_fee = 30
        grand_total = items_total + delivery_fee
        st.write(f"### **Grand Total Bill: ₹{grand_total}**")
        
        person_a = st.text_input("Your Name & Phone Number:")
        address_landmark = st.text_area("Full Delivery Address & Clear Village Landmarks:")
        pay_mode = st.radio("Choose Mode:", ["UPI Online Instant Pay", "Cash on Delivery (COD)"])
        
        if st.button("🏁 Place Final Just Order", type="primary"):
            if person_a and address_landmark:
                time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                p_status_db = "Paid via UPI" if pay_mode == "UPI Online Instant Pay" else "COD Pending"
                conn = sqlite3.connect("just_order_v6.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO orders (shop_name, ordered_by, deliver_to, delivery_address, total_amount, service_type, open_box_required, payment_status, order_time) VALUES (?, ?, ?, ?, ?, 'Hybrid', 0, ?, ?)", (selected_shop_name, person_a, person_a, address_landmark, grand_total, p_status_db, time_now))
                conn.commit()
                conn.close()
                st.success("🎉 Order Registered!")
                st.balloons()
                
                merchant_wa_link = generate_merchant_whatsapp_link(merchant_phone_db, selected_shop_name, person_a, person_a, summary_txt, address_landmark)
                st.markdown(f'<a href="{merchant_wa_link}" target="_blank" style="background-color:#25D366; color:white; padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">💬 Send Live Order Alert to {selected_shop_name}</a>', unsafe_allow_html=True)


    # ==========================================================
    # 🌟 NEW SOCIAL SHARING HUB ENGINE (WhatsApp, FB, Insta)
    # ==========================================================
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Live URL Detection (image_12.png ke browser link ke hisab se setup)
    live_app_url = "https://just-order.streamlit.app" 
    promo_msg = "🔥 Hey! Maine market se khana aur ghar ka rashan mangwane ke liye *Just Order* app use kiya. Delivery sirf 30 min me aur Open Box safety ke sath hoti hai! Aap bhi try karein 👇\n\n" + live_app_url
    
    # URL encodings for sharing
    encoded_promo = urllib.parse.quote(promo_msg)
    encoded_url = urllib.parse.quote(live_app_url)
    
    # Social links structure
    whatsapp_share = f"https://wa.me/?text={encoded_promo}"
    facebook_share = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
    
    st.subheader("📢 Share Just Order with Friends & Family")
    st.write("Apne doston aur parivar ko batayein taaki wo bhi ghar baithe gaon mein saman mangwa sakein! 😎")
    
    # HTML Branded Buttons Grid Layout with Swag CSS Colors
    share_buttons_html = f"""
    <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px;">
        <!-- WHATSAPP BUTTON -->
        <a href="{whatsapp_share}" target="_blank" style="
            background-color: #25D366; color: white; padding: 12px 24px; 
            text-decoration: none; border-radius: 8px; font-weight: bold; 
            font-size: 16px; display: inline-flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">🟢 Share on WhatsApp</a>
        
        <!-- FACEBOOK BUTTON -->
        <a href="{facebook_share}" target="_blank" style="
            background-color: #1877F2; color: white; padding: 12px 24px; 
            text-decoration: none; border-radius: 8px; font-weight: bold; 
            font-size: 16px; display: inline-flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">🔵 Share on Facebook</a>
    </div>
    """
    st.markdown(share_buttons_html, unsafe_allow_html=True)
    
    # INSTAGRAM WORKAROUND INFO (Insta doesn't support web share links directly)
    with st.expander("📸 How to Share on Instagram Stories / Bio?"):
        st.write(f"1. Niche diye gaye link ko **Copy** kar lijiye:\n `{live_app_url}`")
        st.write("2. Apne Instagram App par jaakar **Create Story** par click kijiye.")
        st.write("3. Stickers wale section mein jaakar **'LINK'** sticker select kijiye aur is link ko paste kar dijiye!")
        st.write("🔥 Aap apne Insta Bio mein bhi is link ko daal kar swag dikha sakte hain!")