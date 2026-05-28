import streamlit as st
import sqlite3
import datetime
import os
import urllib.parse

# === 1. DATABASE & FOLDER SETUP ===
def init_db():
    conn = sqlite3.connect("just_order_v5.db")
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
    
    # Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordered_by TEXT NOT NULL,       
            deliver_to TEXT NOT NULL,       
            delivery_address TEXT NOT NULL, 
            total_amount INTEGER NOT NULL,
            service_type TEXT NOT NULL,     
            open_box_required INTEGER,     
            payment_status TEXT DEFAULT 'Pending',
            order_status TEXT DEFAULT 'Received',
            order_time TEXT
        )
    """)
    
    conn.commit()
    conn.close()

    if not os.path.exists("uploaded_images"):
        os.makedirs("uploaded_images")

init_db()

# === WHATSAPP BILL UTILITY FUNCTION ===
def generate_whatsapp_link(phone, name, cart_summary, total_bill, delivery_charge, final_grand_total, pay_status):
    bill_text = f"🚨 *JUST ORDER - INVOICE* 🚨\n\n"
    bill_text += f"👤 *Customer:* {name}\n"
    bill_text += f"--------------------------------\n"
    bill_text += f"📦 *Items Ordered:*\n{cart_summary}\n"
    bill_text += f"--------------------------------\n"
    bill_text += f"💵 *Items Total:* ₹{total_bill}\n"
    bill_text += f"🛵 *Delivery Charge:* ₹{delivery_charge}\n"
    bill_text += f"💰 *Grand Total:* ₹{final_grand_total}\n"
    bill_text += f"💳 *Payment:* {pay_status}\n\n"
    bill_text += f"Thank you for ordering with *Just Order*! 📍"
    
    encoded_text = urllib.parse.quote(bill_text)
    if not phone.startswith('+') and not phone.startswith('91') and len(phone) == 10:
        phone = "91" + phone
    return f"https://wa.me/{phone}?text={encoded_text}"


# === Streamlit Page Design ===
st.set_page_config(page_title="Just Order - Food & Grocery", page_icon="📍", layout="wide")

# === 😎 SWAG LOGO GENERATOR ===
def render_swag_logo():
    logo_html = """
    <div style="
        background: linear-gradient(135deg, #1e1e24 0%, #0a0a0c 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.3);
        margin-bottom: 25px;
        display: inline-block;
        border-left: 6px solid #28a745;
    ">
        <span style="font-family: 'Arial Black', sans-serif; font-size: 42px; font-weight: 900; color: #ffffff; letter-spacing: -1.5px;">JUST</span>
        <span style="font-family: 'Arial Black', sans-serif; font-size: 42px; font-weight: 900; color: #28a745; letter-spacing: -1.5px; background: linear-gradient(to right, #28a745, #85e09b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ORDER</span>
        <span style="font-size: 32px; margin-left: 5px;">📍</span>
        <p style="color: #a0a0a5; margin: 5px 0px 0px 0px; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; font-weight: bold;">Hyperlocal Quick-Commerce Engine</p>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)


# === 2. SIDEBAR CONTROL PANEL ===
st.sidebar.title("🏪 Just Order")
app_mode = st.sidebar.selectbox("Choose Mode:", ["🛒 Customer App", "🔑 Owner Admin Dashboard"])

if app_mode == "🛒 Customer App":
    st.sidebar.markdown("---")
    st.sidebar.write("### 🟢 Live Shop Status")
    conn = sqlite3.connect("just_order_v5.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, status, shop_type, rating FROM shops")
    all_shops = cursor.fetchall()
    
    for shop in all_shops:
        s_id, s_name, s_status, s_type, s_rating = shop
        is_open = st.sidebar.toggle(f"{s_name} ({s_type}) [⭐{s_rating:.1f}]", value=bool(s_status), key=f"sidebar_shop_{s_id}")
        new_status = 1 if is_open else 0
        cursor.execute("UPDATE shops SET status = ? WHERE id = ?", (new_status, s_id))
    conn.commit()
    conn.close()

st.sidebar.markdown("---")
st.sidebar.caption("Just Order v5.4 • Scale Edition")


# ==================================================
# 🛠️ MODE A: OWNER ADMIN DASHBOARD (With Advanced Edit & Delete)
# ==================================================
if app_mode == "🔑 Owner Admin Dashboard":
    render_swag_logo()
    st.write("### 🛡️ Secret Admin Console")
    
    password = st.text_input("Enter Admin Secret Key Password:", type="password")
    
    if password == "suraj123":
        st.success("Access Granted! Welcome back, Founder.")
        
        tab_add_shop, tab_add_item, tab_edit_item, tab_delete_shop, tab_view_orders = st.tabs([
            "➕ Add New Shop", "📸 Upload New Items", "✏️ Change Item Name/Price", "🚨 Delete Shop (Danger Zone)", "📊 View Orders"
        ])
        
        # 1. Add Shop
        with tab_add_shop:
            st.subheader("Register a New Local Shop/Merchant")
            new_shop_name = st.text_input("Enter Shop/Hotel Name:")
            new_shop_type = st.selectbox("Select Shop Category:", ["Food", "Grocery"])
            
            if st.button("🚀 Register Shop", type="primary"):
                if new_shop_name:
                    conn = sqlite3.connect("just_order_v5.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO shops (name, shop_type, status) VALUES (?, ?, 1)", (new_shop_name, new_shop_type))
                    conn.commit()
                    conn.close()
                    st.success(f"Registered: **{new_shop_name}**!")
                
        # 2. Add Items
        with tab_add_item:
            st.subheader("Add Products to Shop")
            conn = sqlite3.connect("just_order_v5.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, shop_type FROM shops")
            existing_shops = cursor.fetchall()
            
            if existing_shops:
                shop_map = {f"{s[1]} ({s[2]})": s[0] for s in existing_shops}
                target_shop = st.selectbox("Select Target Shop:", list(shop_map.keys()), key="add_item_shop_select")
                target_shop_id = shop_map[target_shop]
                
                new_item_name = st.text_input("Enter Item Name:", placeholder="e.g. Rasgulla, Mustard Oil 1L")
                new_item_price = st.number_input("Enter Price (INR):", min_value=1, value=10)
                uploaded_file = st.file_uploader("Choose a Photo (JPG/PNG):", type=["jpg", "png", "jpeg"])
                
                if st.button("➕ Upload & Inject Item"):
                    if new_item_name:
                        saved_image_path = None
                        if uploaded_file is not None:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            clean_name = new_item_name.replace(" ", "_")
                            file_name = f"{timestamp}_{clean_name}.jpg"
                            saved_image_path = os.path.join("uploaded_images", file_name)
                            with open(saved_image_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        
                        cursor.execute("INSERT INTO items (shop_id, item_name, price, item_image) VALUES (?, ?, ?, ?)", 
                                       (target_shop_id, new_item_name, new_item_price, saved_image_path))
                        conn.commit()
                        st.success(f"Added **{new_item_name}** into Database!")
            else:
                st.info("Pehle ek dukaan register kijiye.")
            conn.close()

        # 🌟 FEATURE 1 FIXED: SHOP-WISE ITEM FILTER AND MODIFY TAB
        with tab_edit_item:
            st.subheader("✏️ Modify/Change Item Details by Selecting Shop First")
            conn = sqlite3.connect("just_order_v5.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, shop_type FROM shops")
            all_shops_for_edit = cursor.fetchall()
            
            if all_shops_for_edit:
                edit_shop_map = {f"{s[1]} ({s[2]})": s[0] for s in all_shops_for_edit}
                selected_shop_label = st.selectbox("Step 1: Select Shop Name:", list(edit_shop_map.keys()), key="edit_item_shop_select")
                selected_shop_id_edit = edit_shop_map[selected_shop_label]
                
                # Filter items belonging ONLY to this shop
                cursor.execute("SELECT id, item_name, price FROM items WHERE shop_id=?", (selected_shop_id_edit,))
                filtered_items = cursor.fetchall()
                
                if filtered_items:
                    item_map = {f"{it[1]} (Current: ₹{it[2]})": it[0] for it in filtered_items}
                    selected_item_label = st.selectbox("Step 2: Choose Item to Change:", list(item_map.keys()))
                    target_item_id = item_map[selected_item_label]
                    
                    cursor.execute("SELECT item_name, price FROM items WHERE id=?", (target_item_id,))
                    current_name_db, current_price_db = cursor.fetchone()
                    
                    updated_name = st.text_input("Change Item Name To:", value=current_name_db)
                    updated_price = st.number_input("Change Price (INR) To:", min_value=1, value=current_price_db)
                    
                    if st.button("💾 Save Modified Updates", type="primary"):
                        cursor.execute("UPDATE items SET item_name=?, price=? WHERE id=?", (updated_name, updated_price, target_item_id))
                        conn.commit()
                        st.success(f"Success! Item changes updated in Database.")
                else:
                    st.warning("⚠️ Is dukan ke andar abhi koi item nahi joda gaya hai!")
            else:
                st.info("No shops available.")
            conn.close()
            
        # 🌟 FEATURE 2 EXPLICIT: SHOP DELETE OPTION (DANGER ZONE)
        with tab_delete_shop:
            st.subheader("🚨 Delete Local Shop from Database")
            st.write("Warning: Kisi dukan ko delete karne se uske andar ke saare menu items bhi automatic delete ho jayenge!")
            
            conn = sqlite3.connect("just_order_v5.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, shop_type FROM shops")
            all_shops_for_del = cursor.fetchall()
            
            if all_shops_for_del:
                del_shop_map = {f"{s[1]} ({s[2]})": s[0] for s in all_shops_for_del}
                selected_shop_del = st.selectbox("Select Shop to Permanently Delete:", list(del_shop_map.keys()))
                target_shop_id_del = del_shop_map[selected_shop_del]
                
                # Double verification safety check box
                confirm_del = st.checkbox(f"Yes, I want to completely delete {selected_shop_del} from Just Order.")
                
                if st.button("🗑️ Permanently Delete Shop", type="primary"):
                    if confirm_del:
                        # 1. Delete items of that shop first
                        cursor.execute("DELETE FROM items WHERE shop_id=?", (target_shop_id_del,))
                        # 2. Delete the shop itself
                        cursor.execute("DELETE FROM shops WHERE id=?", (target_shop_id_del,))
                        conn.commit()
                        st.success(f"🗑️ Successfully Deleted **{selected_shop_del}** and all its food/grocery items!")
                    else:
                        st.error("Please tick the confirmation checkbox before clicking delete.")
            else:
                st.info("No registered shops found to delete.")
            conn.close()

        with tab_view_orders:
            st.subheader("📊 Live Order Ledger")
            conn = sqlite3.connect("just_order_v5.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders ORDER BY order_id DESC")
            orders_rows = cursor.fetchall()
            
            if orders_rows:
                for row in orders_rows:
                    o_id, o_by, d_to, addr, amt, s_type, ob_req, p_status, o_status, o_time = row
                    with st.expander(f"📦 Order #{o_id} for {d_to} - Total: ₹{amt}"):
                        st.write(f"**Address:** {addr} | **Status:** `{p_status}`")
                        if "COD" in p_status or "Cash" in p_status:
                            phone_num = d_to.split("-")[-1].strip() if "-" in d_to else "0000000000"
                            manual_wa_url = generate_whatsapp_link(phone_num, d_to, "Package Delivered", amt-30, 30, amt, "✅ Paid Cash")
                            st.markdown(f'<a href="{manual_wa_url}" target="_blank" style="background-color:#007bff; color:white; padding:8px 16px; text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block;">🟢 Delivery Boy: Send Cash Bill on WhatsApp</a>', unsafe_allow_html=True)
            else:
                st.info("No orders received yet.")
            conn.close()


# ==========================================
# 🛒 MODE B: THE MAIN CUSTOMER APP
# ==========================================
else:
    render_swag_logo()
    st.write("### *Ek hi App se Sab Kuch Mangwayein!*")
    
    tab_food, tab_grocery, tab_ratings = st.tabs(["🍔 Order Food (Zomato Style)", "🥦 Order Grocery & Veggies (Blinkit Style)", "⭐ Rate Local Shopkeepers"])
    
    # --- TAB 1: FOOD DELIVERY ENGINE ---
    with tab_food:
        st.header("Hot & Fresh Food Delivery")
        conn = sqlite3.connect("just_order_v5.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status FROM shops WHERE shop_type='Food'")
        food_shops = cursor.fetchall()
        
        cart_food = {}
        if food_shops:
            food_options = {f[1]: (f[0], f[2]) for f in food_shops}
            selected_food_shop = st.selectbox("Choose Restaurant:", list(food_options.keys()), key="food_box")
            f_id, f_status = food_options[selected_food_shop]
            
            if f_status == 0:
                st.error(f"❌ Sorry, {selected_food_shop} is currently closed.")
            else:
                st.success(f"Active Menu of {selected_food_shop}")
                cursor.execute("SELECT id, item_name, price, item_image FROM items WHERE shop_id=?", (f_id,))
                f_items = cursor.fetchall()
                
                c1, c2 = st.columns(2)
                for idx, item in enumerate(f_items):
                    i_id, i_name, i_price, i_img = item
                    col = c1 if idx % 2 == 0 else c2
                    with col:
                        if i_img and os.path.exists(i_img):
                            st.image(i_img, caption=i_name, width=220)
                        else:
                            st.image("https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&auto=format&fit=crop&q=60", caption="Just Order Special", width=220)
                        qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"f_item_{i_id}")
                        if qty > 0:
                            cart_food[i_name] = {"price": i_price, "qty": qty, "type": "Zomato (Food)"}
                        st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Admin dashboard mein jaakar pehle Food dukan register karein.")
        conn.close()

    # --- TAB 2: GROCERY ENGINE ---
    with tab_grocery:
        st.header("10-Minute Grocery Delivery")
        conn = sqlite3.connect("just_order_v5.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status FROM shops WHERE shop_type='Grocery'")
        grocery_shops = cursor.fetchall()
        
        cart_grocery = {}
        if grocery_shops:
            grocery_options = {g[1]: (g[0], g[2]) for g in grocery_shops}
            selected_grocery_shop = st.selectbox("Choose Grocery Store:", list(grocery_options.keys()), key="grocery_box")
            g_id, g_status = grocery_options[selected_grocery_shop]
            
            if g_status == 0:
                st.error(f"❌ Sorry, {selected_grocery_shop} is currently closed.")
            else:
                st.success(f"Active Menu of {selected_grocery_shop}")
                cursor.execute("SELECT id, item_name, price, item_image FROM items WHERE shop_id=?", (g_id,))
                g_items = cursor.fetchall()
                
                c1, c2 = st.columns(2)
                for idx, item in enumerate(g_items):
                    i_id, i_name, i_price, i_img = item
                    col = c1 if idx % 2 == 0 else c2
                    with col:
                        if i_img and os.path.exists(i_img):
                            st.image(i_img, caption=i_name, width=220)
                        else:
                            st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&auto=format&fit=crop&q=60", caption="Just Order Grocery", width=220)
                        qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"g_item_{i_id}")
                        if qty > 0:
                            cart_grocery[i_name] = {"price": i_price, "qty": qty, "type": "Blinkit (Grocery)"}
                        st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Admin dashboard mein jaakar pehle Grocery dukan register karein.")
        conn.close()

    # --- TAB 3: RATINGS ---
    with tab_ratings:
        st.header("⭐ Rate Your Local Shopkeepers")
        conn = sqlite3.connect("just_order_v5.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM shops")
        all_shops_list = cursor.fetchall()
        
        if all_shops_list:
            rating_options = {s[1]: s[0] for s in all_shops_list}
            target_shop_name = st.selectbox("Select Shop to Rate:", list(rating_options.keys()))
            target_shop_id = rating_options[target_shop_name]
            stars = st.slider("Rate from 1 to 5 Stars:", min_value=1, max_value=5, value=5)
            
            if st.button("Submit Rating", type="secondary"):
                cursor.execute("SELECT rating, rating_count FROM shops WHERE id=?", (target_shop_id,))
                current_rating, current_count = cursor.fetchone()
                new_count = current_count + 1
                new_rating = ((current_rating * current_count) + stars) / new_count
                cursor.execute("UPDATE shops SET rating=?, rating_count=? WHERE id=?", (new_rating, new_count, target_shop_id))
                conn.commit()
                st.success(f"Thank you! You rated **{target_shop_name}** with {stars} Stars.")
        conn.close()

    # --- GLOBAL CART COMBINATION & CHECKOUT ---
    final_cart = {**cart_food, **cart_grocery}

    if final_cart:
        st.markdown("---")
        st.subheader("🛍️ Your Combined Just Order Cart")
        
        total_items_price = 0
        service_type_tag = ""
        cart_summary_text = ""
        
        for item_name, info in final_cart.items():
            cost = info['price'] * info['qty']
            total_items_price += cost
            service_type_tag = info['type']
            cart_summary_text += f"• {item_name} x {info['qty']} (₹{cost})\n"
            st.write(f"• [{info['type']}] **{item_name}** x {info['qty']} = ₹{cost}")
            
        delivery_fee = 30
        grand_total = total_items_price + delivery_fee
        
        st.write(f"Items Total: ₹{total_items_price}")
        st.write(f"🛵 **Delivery Charge: ₹{delivery_fee}**")
        st.write(f"### **Grand Total Bill: ₹{grand_total} (Tax Incl.)**")
        
        st.markdown("---")
        st.subheader("🛡️ Safety & Quality Check")
        open_box_delivery = st.checkbox("📦 Request Open Box Delivery (Highly Recommended for Grocery/Veggies!)")
        
        st.subheader("📍 Contact & Address Registry")
        person_a = st.text_input("Sender Name & Phone (Person A):", placeholder="Suraj Kumar - 9876543210")
        is_gift = st.checkbox("🎁 Sending this order to someone else? (Deliver to Person B)")
        
        if is_gift:
            person_b = st.text_input("Receiver Name & Phone (Person B):", placeholder="Amit Kumar - 8877665544")
            address = st.text_area("Person B Address & Village Landmarks:")
        else:
            person_b = person_a
            address = st.text_area("Your Delivery Address:")
            
        payment_choice = st.radio("Select Payment Mode:", ["UPI Online Instant Pay", "Cash on Delivery (COD)"])
        
        phone_to_send = person_b.split("-")[-1].strip() if "-" in person_b else "0000000000"
        auto_wa_url = generate_whatsapp_link(phone_to_send, person_b, cart_summary_text, total_items_price, delivery_fee, grand_total, "✅ Paid via UPI Online")
        
        if payment_choice == "UPI Online Instant Pay":
            upi_url = f"upi://pay?pa=justorder@upi&pn=JustOrderV2&am={grand_total}&cu=INR"
            st.markdown(f'<a href="{upi_url}" style="background-color:#28a745; color:white; padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">🚀 Pay ₹{grand_total} Now</a>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🏁 Place Final Just Order", type="primary"):
            if not person_a or not address or (is_gift and not person_b):
                st.error("Fields khali hain! Please address aur phone number bharo.")
            else:
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                open_box_flag = 1 if open_box_delivery else 0
                pay_status_db = "Online Paid" if payment_choice == "UPI Online Instant Pay" else "COD Pending"
                
                conn = sqlite3.connect("just_order_v5.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (ordered_by, deliver_to, delivery_address, total_amount, service_type, open_box_required, payment_status, order_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (person_a, person_b, address, grand_total, service_type_tag, open_box_flag, pay_status_db, time_stamp))
                conn.commit()
                conn.close()
                
                st.success(f"🎉 Awesome! Your order has been registered successfully.")
                st.balloons()
                
                if payment_choice == "UPI Online Instant Pay":
                    st.info("📲 Redirecting to WhatsApp to send automatic digital bill...")
                    st.markdown(f'<a href="{auto_wa_url}" target="_blank" style="background-color:#25D366; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block;">💬 Open WhatsApp & Send Bill Instantly</a>', unsafe_allow_html=True)