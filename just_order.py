import streamlit as st
import sqlite3
import datetime
import os
import urllib.parse

# === 1. ADVANCED DATABASE SETUP ===
def init_db():
    conn = sqlite3.connect("just_order_v5.db")
    cursor = conn.cursor()
    
    # Shops Table (With shop_phone for instant routing)
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
    
    # Orders Table (With Shop context and Rider tracking updates)
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
    
    # Initial Dummy Data Check with Default Test Phone Strings
    cursor.execute("SELECT COUNT(*) FROM shops")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO shops (name, shop_type, shop_phone, status) VALUES ('Nalanda Sweets & Chat Corner', 'Food', '910000000000', 1)")
        cursor.execute("INSERT INTO shops (name, shop_type, shop_phone, status) VALUES ('Kalyanpur Kirana Store', 'Grocery', '910000000000', 1)")
        cursor.execute("INSERT INTO items (shop_id, item_name, price) VALUES (1, 'Special Samosa (1 Plate)', 20)")
        cursor.execute("INSERT INTO items (shop_id, item_name, price) VALUES (2, 'Fortune Mustard Oil (1L)', 175)")
        
    conn.commit()
    conn.close()

    if not os.path.exists("uploaded_images"):
        os.makedirs("uploaded_images")

init_db()

# === WHATSAPP LINK GENERATORS ===
def generate_whatsapp_link(phone, name, cart_summary, total_bill, delivery_charge, final_grand_total, pay_status):
    bill_text = f"🚨 *JUST ORDER - INVOICE* 🚨\n\n"
    bill_text += f"👤 *Customer:* {name}\n"
    bill_text += f"📅 *Date/Time:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
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

def generate_merchant_whatsapp_link(merchant_phone, shop_name, customer_name, customer_phone, items_summary, address_landmark):
    msg_text = f"🚨 *JUST ORDER - NEW ORDER RECEIVED* 🚨\n\n"
    msg_text += f"🏪 *Shop:* {shop_name}\n"
    msg_text += f"--------------------------------\n"
    msg_text += f"📦 *Order Items & Qty:*\n{items_summary}\n"
    msg_text += f"--------------------------------\n"
    msg_text += f"👤 *Customer:* {customer_name}\n"
    msg_text += f"📞 *Customer Call Direct Link:* tel:{customer_phone}\n"
    msg_text += f"📍 *Delivery Landmark:* {address_landmark}\n\n"
    msg_text += f"Dukanadar bhai, kripya jaldi se items pack kijiye! 🍳🎒"
    return f"https://wa.me/{merchant_phone}?text={urllib.parse.quote(msg_text)}"

def generate_rider_whatsapp_link(rider_phone, rider_name, o_id, shop, customer_name, address, cash_amt):
    rider_msg = f"🛵 *JUST ORDER - NEW TASK ASSIGNED* 🛵\n\n"
    rider_msg += f"👤 *Rider Name:* {rider_name}\n"
    rider_msg += f"🆔 *Order ID:* #{o_id}\n"
    rider_msg += f"--------------------------------\n"
    rider_msg += f"🏪 *Pickup Shop:* {shop}\n"
    rider_msg += f"👤 *Deliver To:* {customer_name}\n"
    rider_msg += f"📍 *Landmark Destination Address:* {address}\n"
    rider_msg += f"💵 *Collect Cash Total:* ₹{cash_amt}\n"
    rider_msg += f"--------------------------------\n"
    rider_msg += f"Safe ride kijiye aur on-time deliver kijiye! 🏁"
    return f"https://wa.me/{rider_phone}?text={urllib.parse.quote(rider_msg)}"


# === Streamlit Page Layout ===
st.set_page_config(page_title="Just Order - Food & Grocery", page_icon="📍", layout="wide")

# 😎 SWAG LOGO GENERATOR
def render_swag_logo():
    logo_html = """
    <div style="background: linear-gradient(135deg, #1e1e24 0%, #0a0a0c 100%); padding: 20px; border-radius: 15px; box-shadow: 0px 8px 16px rgba(0,0,0,0.3); margin-bottom: 25px; display: inline-block; border-left: 6px solid #28a745;">
        <span style="font-family: 'Arial Black', sans-serif; font-size: 42px; font-weight: 900; color: #ffffff; letter-spacing: -1.5px;">JUST</span>
        <span style="font-family: 'Arial Black', sans-serif; font-size: 42px; font-weight: 900; color: #28a745; letter-spacing: -1.5px; background: linear-gradient(to right, #28a745, #85e09b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ORDER</span>
        <span style="font-size: 32px; margin-left: 5px;">📍</span>
        <p style="color: #a0a0a5; margin: 5px 0px 0px 0px; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; font-weight: bold;">Hyperlocal Quick-Commerce Engine</p>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

# 📢 SOCIAL MEDIA SHARING FOOTER
def render_social_share_buttons():
    app_url = "https://just-order-cg2hmpqhgebmvbdkjvgynh.streamlit.app/"
    share_text = "Ab market ka khana aur ghar ka rashan mangwao seedhe ghar baithe Just Order App se! Try karo abhi: "
    whatsapp_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_text + app_url)}"
    facebook_share = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(app_url)}"
    
    share_html = f"""
    <div style="margin-top: 50px; margin-bottom: 20px; background-color: #f8f9fa; padding: 20px; border-radius: 12px; box-shadow: 0px 2px 8px rgba(0,0,0,0.05); text-align: center;">
        <strong style="color: #333; font-family: sans-serif; font-size: 15px; display: block; margin-bottom: 12px;">📢 Just Order App Apne Doston aur Parivar ko Share Karein:</strong>
        <a href="{whatsapp_share}" target="_blank" style="background-color: #25D366; color: white; padding: 10px 22px; text-decoration: none; border-radius: 20px; font-weight: bold; font-family: sans-serif; font-size: 13px; margin-right: 8px; display: inline-block;">🟢 WhatsApp Share</a>
        <a href="{facebook_share}" target="_blank" style="background-color: #1877F2; color: white; padding: 10px 22px; text-decoration: none; border-radius: 20px; font-weight: bold; font-family: sans-serif; font-size: 13px; margin-right: 8px; display: inline-block;">🔵 Facebook Share</a>
        <button onclick="navigator.clipboard.writeText('{app_url}'); alert('App Link Copied! Bio me paste karein. 😎');" style="background-color: #E1306C; color: white; padding: 10px 22px; border: none; border-radius: 20px; font-weight: bold; font-family: sans-serif; font-size: 13px; cursor: pointer; display: inline-block;">🟣 Copy for Instagram</button>
    </div>
    """
    st.markdown(share_html, unsafe_allow_html=True)


if "screen_view" not in st.session_state:
    st.session_state.screen_view = "menu_screen"
if "global_cart" not in st.session_state:
    st.session_state.global_cart = {}
if "service_tag" not in st.session_state:
    st.session_state.service_tag = ""
if "selected_shop_name" not in st.session_state:
    st.session_state.selected_shop_name = ""
if "merchant_phone" not in st.session_state:
    st.session_state.merchant_phone = ""


# === 2. SIDEBAR NAVIGATION ===
st.sidebar.title("🏪 Just Order")
app_mode = st.sidebar.selectbox("Choose Mode:", ["🛒 Customer App", "🔑 Owner Admin Dashboard"])

if app_mode == "🛒 Customer App" and st.session_state.screen_view == "menu_screen":
    st.sidebar.markdown("---")
    st.sidebar.write("### 🟢 Live Shop Status")
    conn = sqlite3.connect("just_order_v6.db")
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
st.sidebar.caption("Just Order v7.1 • Multi-Notification Platform")


# ==================================================
# 🔑 MODE A: OWNER & DISPATCH CONTROL PANEL
# ==================================================
if app_mode == "🔑 Owner Admin Dashboard":
    render_swag_logo()
    st.write("### 🛡️ Secret Admin Console")
    password = st.text_input("Enter Admin Secret Key Password:", type="password")
    
    if password == "suraj123":
        st.success("Access Granted! Welcome back, Founder.")
        tab_dispatch, tab_merchant_phone, tab_add_shop, tab_add_item, tab_edit_item = st.tabs([
            "🛵 1. Rider Dispatch Hub", "📞 2. Register Merchant Phone", "➕ 3. Add New Shop", "📸 4. Upload Items", "✏️ 5. Edit Price"
        ])
        
        # 🌟 LOGISTICS HUB FOR RIDERS
        with tab_dispatch:
            st.subheader("🛵 Active Deliveries Router")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT order_id, shop_name, ordered_by, total_amount, order_status, delivery_address, delivery_boy FROM orders ORDER BY order_id DESC")
            all_orders = cursor.fetchall()
            
            if all_orders:
                for o_row in all_orders:
                    o_id, s_name, o_by, amt, o_stat, addr, d_boy = o_row
                    with st.expander(f"📦 Order #{o_id} [{o_stat}] - {o_by}"):
                        st.write(f"🏠 *Merchant Point:* **{s_name}**")
                        st.write(f"📍 *Landmark Destination Address:* **{addr}**")
                        st.write(f"💰 *Collect Bill Cash:* **₹{amt}**")
                        st.write(f"🚴 *Assigned Boy:* `{d_boy}`")
                        
                        # Dispatch assignment elements
                        rider_profile = st.selectbox(f"Select Rider for #{o_id}:", ["Amit Kumar (918877665544)", "Ranjan Kumar (917766554433)", "Suraj Kumar (916204051301)"], key=f"rider_select_{o_id}")
                        
                        if st.button(f"🔒 Assign Rider to Task #{o_id}"):
                            cursor.execute("UPDATE orders SET delivery_boy=?, order_status='Out for Delivery 🛵' WHERE order_id=?", (rider_profile, o_id))
                            conn.commit()
                            st.success(f"Rider assigned to order #{o_id}!")
                            st.rerun()
                        
                        # 🌟 DYNAMIC NOTIFICATION FOR THE DELIVER BOY
                        if d_boy != 'Not Assigned ❌':
                            rider_name = d_boy.split("(")[0].strip()
                            rider_phone = d_boy.split("(")[-1].replace(")", "").strip()
                            cust_name_only = o_by.split("-")[0].strip()
                            
                            rider_wa_link = generate_rider_whatsapp_link(
                                rider_phone=rider_phone, rider_name=rider_name, o_id=o_id, 
                                shop=s_name, customer_name=cust_name_only, address=addr, cash_amt=amt
                            )
                            st.markdown(f'<a href="{rider_wa_link}" target="_blank" style="background-color:#ffc107; color:black; padding:8px 16px; text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block; margin-top:10px;">📲 Send Task to Delivery Boy via WhatsApp</a>', unsafe_allow_html=True)
            conn.close()

        with tab_merchant_phone:
            st.subheader("📞 Link Active WhatsApp Numbers to Shopkeepers")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, shop_phone FROM shops")
            all_shops_list = cursor.fetchall()
            if all_shops_list:
                shop_map_phone = {f"{s[1]} (Phone: {s[2]})": s[0] for s in all_shops_list}
                selected_shop_ph = st.selectbox("Select Merchant Target:", list(shop_map_phone.keys()))
                target_shop_id_ph = shop_map_phone[selected_shop_ph]
                new_phone_num = st.text_input("Enter Merchant WhatsApp Number (with 91 prefix, e.g. 916204051301):")
                if st.button("💾 Link Phone Context to Shop"):
                    if new_phone_num:
                        cursor.execute("UPDATE shops SET shop_phone=? WHERE id=?", (new_phone_num, target_shop_id_ph))
                        conn.commit()
                        st.success("Successfully Linked WhatsApp Channel!")
            conn.close()

        with tab_add_shop:
            st.subheader("Register a New Local Shop/Merchant")
            new_shop_name = st.text_input("Enter Shop/Hotel Name:")
            new_shop_type = st.selectbox("Select Shop Category:", ["Food", "Grocery"])
            if st.button("🚀 Register Shop", type="primary"):
                if new_shop_name:
                    conn = sqlite3.connect("just_order_v6.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO shops (name, shop_type, status) VALUES (?, ?, 1)", (new_shop_name, new_shop_type))
                    conn.commit()
                    conn.close()
                    st.success(f"Registered: **{new_shop_name}**!")
                
        with tab_add_item:
            st.subheader("Add Products by Uploading Local Image File")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, shop_type FROM shops")
            existing_shops = cursor.fetchall()
            if existing_shops:
                shop_map = {f"{s[1]} ({s[2]})": s[0] for s in existing_shops}
                target_shop = st.selectbox("Select Target Shop:", list(shop_map.keys()), key="add_it_shop")
                target_shop_id = shop_map[target_shop]
                new_item_name = st.text_input("Enter Item Name:", placeholder="Your Name")
                new_item_price = st.number_input("Enter Price (INR):", min_value=1, value=10)
                uploaded_file = st.file_uploader("Choose a Photo:", type=["jpg", "png", "jpeg"])
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
                        st.success(f"Added **{new_item_name}** successfully!")
            conn.close()

        with tab_edit_item:
            st.subheader("✏️ Modify Item Details")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, item_name, price FROM items")
            all_current_items = cursor.fetchall()
            if all_current_items:
                item_map = {f"{it[1]} (Current: ₹{it[2]})": it[0] for it in all_current_items}
                selected_item_label = st.selectbox("Choose Item to Change:", list(item_map.keys()))
                target_item_id = item_map[selected_item_label]
                cursor.execute("SELECT item_name, price FROM items WHERE id=?", (target_item_id,))
                current_name_db, current_price_db = cursor.fetchone()
                updated_name = st.text_input("Change Item Name To:", value=current_name_db)
                updated_price = st.number_input("Change Price (INR) To:", min_value=1, value=current_price_db)
                if st.button("💾 Save Modified Updates", type="primary"):
                    cursor.execute("UPDATE items SET item_name=?, price=? WHERE id=?", (updated_name, updated_price, target_item_id))
                    conn.commit()
                    st.success(f"Success! Updated details saved in Database.")
            conn.close()


# ==========================================
# 🛒 MODE B: THE MAIN CUSTOMER INTERFACE
# ==========================================
else:
    render_swag_logo()

    # --------------------------------------------------
    # 🏁 SCREEN TWO: DEDICATED BILLING & CHECKOUT PAGE
    # --------------------------------------------------
    if st.session_state.screen_view == "billing_screen":
        st.title("🛍️ Secure Checkout & Bill Summary")
        if st.button("⬅️ Back to Menu / Add More Items"):
            st.session_state.screen_view = "menu_screen"
            st.rerun()
            
        st.write("---")
        total_items_price = 0
        cart_summary_text = ""
        for item_name, info in st.session_state.global_cart.items():
            cost = info['price'] * info['qty']
            total_items_price += cost
            cart_summary_text += f"• {item_name} x {info['qty']} = ₹{cost}\n"
            st.write(f"🔹 **{item_name}** x  {info['qty']} Pcs = **₹{cost}**", unsafe_allow_html=True)
            
        delivery_fee = 30
        grand_total = total_items_price + delivery_fee
        
        st.markdown("---")
        st.write(f"📋 Items Total Cost: **₹{total_items_price}**")
        st.write(f"🛵 Fixed Delivery Fee: **₹{delivery_fee}**")
        st.write(f"### 💰 Net Payable Grand Total: ₹{grand_total}")
        
        st.write("---")
        st.subheader("📍 Contact & Address Registry")
        person_a_name = st.text_input("Your Full Name *", placeholder="Your Name")
        person_a_phone = st.text_input("10-Digit Mobile Number *", placeholder="Your Phone Number")
        address_landmark = st.text_area("Full Delivery Address & Clear Village Landmarks *", placeholder="Your Address")
        
        payment_choice = st.radio("Select Payment Mode:", ["UPI Online Instant Pay", "Cash on Delivery (COD)"])
        
        if payment_choice == "UPI Online Instant Pay":
            upi_url = f"upi://pay?pa=suraj.u7870-1@oksbi&pn=Just+Order&am={grand_total}&cu=INR"
            st.markdown(f'<a href="{upi_url}" style="background-color:#28a745; color:white; padding:14px 28px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block; font-size:16px;">🚀 Pay ₹{grand_total} Now via UPI</a>', unsafe_allow_html=True)
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("🏁 Confirm & Place Final Just Order", type="primary", use_container_width=True):
            if not person_a_name.strip() or not person_a_phone.strip() or not address_landmark.strip():
                st.error("⚠️ Sabhi fields bharna anivarya (mandatory) hai! Kripya details khali na chhorein.")
            elif len(person_a_phone.strip()) < 10:
                st.error("⚠️ Mobile number kam se kam 10 anko ka hona chahiye!")
            else:
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pay_status_db = "Online Paid" if payment_choice == "UPI Online Instant Pay" else "COD Pending"
                person_final_combined = f"{person_a_name} - {person_a_phone}"
                
                conn = sqlite3.connect("just_order_v6.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (shop_name, ordered_by, deliver_to, delivery_address, total_amount, service_type, open_box_required, payment_status, order_time)
                    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """, (st.session_state.selected_shop_name, person_final_combined, person_final_combined, address_landmark, grand_total, st.session_state.service_tag, pay_status_db, time_stamp))
                conn.commit()
                conn.close()
                
                st.success(f"🎉 Awesome! Your order has been registered successfully.")
                st.balloons()
                
                # 🌟 TRIGGER A: WHATSAPP ALERT FOR BUSY SHOPKEEPER
                merchant_wa_url = generate_merchant_whatsapp_link(
                    merchant_phone=st.session_state.merchant_phone,
                    shop_name=st.session_state.selected_shop_name,
                    customer_name=person_a_name,
                    customer_phone=person_a_phone.strip(),
                    items_summary=cart_summary_text,
                    address_landmark=address_landmark
                )
                
                st.markdown("### 🔔 Alert Dukandar Instantly")
                st.info("Niche diye gaye WhatsApp button par click karein taaki dukandar bhai ko turant items aur customer call details ka notification mil jaye!")
                st.markdown(f'<a href="{merchant_wa_link}" target="_blank" style="background-color:#25D366; color:white; padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block; font-size:16px;">💬 Send Live Order Alert to Shopkeeper</a>', unsafe_allow_html=True)
                
                # Clear session storage maps post checkout
                st.session_state.global_cart = {}


    # --------------------------------------------------
    # 🍔 SCREEN ONE: SHOP MENU & PRODUCT SELECTION PAGE
    # --------------------------------------------------
    else:
        st.write("### *Ek hi App se Sab Kuch Mangwayein!*")
        tab_food, tab_grocery, tab_ratings = st.tabs(["🍔 Order Food (Zomato Style)", "🥦 Order Grocery & Veggies (Blinkit Style)", "⭐ Rate Local Shopkeepers"])
        
        cart_food = {}
        cart_grocery = {}
        service_tag_local = ""
        
        with tab_food:
            st.header("Hot & Fresh Food Delivery")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, status, shop_phone FROM shops WHERE shop_type='Food'")
            food_shops = cursor.fetchall()
            
            if food_shops:
                food_options = {f[1]: (f[0], f[2], f[3]) for f in food_shops}
                selected_food_shop = st.selectbox("Choose Restaurant:", list(food_options.keys()), key="food_box")
                f_id, f_status, f_phone = food_options[selected_food_shop]
                
                if f_status == 0:
                    st.error(f"❌ Sorry, {selected_food_shop} is currently closed.")
                else:
                    st.success(f"Active Menu of {selected_food_shop}")
                    
                    # Store variables globally in session state
                    st.session_state.selected_shop_name = selected_food_shop
                    st.session_state.merchant_phone = f_phone
                    
                    cursor.execute("SELECT id, item_name, price, item_image FROM items WHERE shop_id=?", (f_id,))
                    c1, c2 = st.columns(2)
                    for idx, item in enumerate(cursor.fetchall()):
                        i_id, i_name, i_price, i_img = item
                        col = c1 if idx % 2 == 0 else c2
                        with col:
                            st.image("https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&auto=format&fit=crop&q=60", width=160)
                            qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"f_item_{i_id}")
                            if qty > 0:
                                cart_food[i_name] = {"price": i_price, "qty": qty, "type": "Zomato (Food)"}
                                service_tag_local = "Zomato (Food)"
            conn.close()

        with tab_grocery:
            st.header("10-Minute Grocery Delivery")
            conn = sqlite3.connect("just_order_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, status, shop_phone FROM shops WHERE shop_type='Grocery'")
            grocery_shops = cursor.fetchall()
            
            if grocery_shops:
                grocery_options = {g[1]: (g[0], g[2], g[3]) for g in grocery_shops}
                selected_grocery_shop = st.selectbox("Choose Grocery Store:", list(grocery_options.keys()), key="grocery_box")
                g_id, g_status, g_phone = grocery_options[selected_grocery_shop]
                
                if g_status == 0:
                    st.error(f"❌ Sorry, {selected_grocery_shop} is currently closed.")
                else:
                    st.success(f"Active Menu of {selected_grocery_shop}")
                    
                    if not cart_food:
                        st.session_state.selected_shop_name = selected_grocery_shop
                        st.session_state.merchant_phone = g_phone
                        
                    cursor.execute("SELECT id, item_name, price, item_image FROM items WHERE shop_id=?", (g_id,))
                    c1, c2 = st.columns(2)
                    for idx, item in enumerate(cursor.fetchall()):
                        i_id, i_name, i_price, i_img = item
                        col = c1 if idx % 2 == 0 else c2
                        with col:
                            st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&auto=format&fit=crop&q=60", width=160)
                            qty = st.number_input(f"{i_name} (₹{i_price})", min_value=0, max_value=10, key=f"g_item_{i_id}")
                            if qty > 0:
                                cart_grocery[i_name] = {"price": i_price, "qty": qty, "type": "Blinkit (Grocery)"}
                                service_tag_local = "Blinkit (Grocery)"
            conn.close()

        with tab_ratings:
            st.header("⭐ Rate Your Local Shopkeepers")
            conn = sqlite3.connect("just_order_v6.db")
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
                    st.success(f"Thank you!")
            conn.close()

        merged_cart = {**cart_food, **cart_grocery}
        if merged_cart:
            st.markdown("---")
            if st.button("🚀 Proceed to Checkout / View Bill Summary", type="primary", use_container_width=True):
                st.session_state.global_cart = merged_cart
                st.session_state.service_tag = service_tag_local if service_tag_local else "Hybrid Delivery"
                st.session_state.screen_view = "billing_screen"
                st.rerun()

    # Shared Marketing Panel Footer at extreme bottom
    st.write("---")
    render_social_share_buttons()