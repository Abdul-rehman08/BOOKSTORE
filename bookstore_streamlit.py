import streamlit as st
import pandas as pd
from datetime import datetime

# --- Initialize session state ---
if "book_ids" not in st.session_state:
    st.session_state.book_ids = [1, 2, 3, 4, 5]
    st.session_state.titles = ["Python Basics", "AI & ML", "Data Science", "Web Development", "Cyber Security"]
    st.session_state.stocks = [10, 5, 8, 6, 4]
    st.session_state.prices = [250, 400, 300, 350, 500]
    st.session_state.logged_in_admin = False
    st.session_state.users = {"user1": "pass1"}  # username: password
    st.session_state.current_user = None
    st.session_state.sales = []  # List of dicts

# --- Admin credentials ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# --- Utility function ---
def get_books_df():
    return pd.DataFrame({
        "ID": st.session_state.book_ids,
        "Title": st.session_state.titles,
        "Stock": st.session_state.stocks,
        "Price (Rs.)": st.session_state.prices
    })

# --- Sidebar ---
st.sidebar.title("📚 Book Store Navigation")
menu = st.sidebar.radio("Go to", ["Home", "Buy a Book", "Login", "Admin Panel"])

# --- Home / Book Listing ---
if menu == "Home":
    st.title("📚 Available Books")
    search = st.text_input("🔍 Search by title")
    df = get_books_df()
    if search:
        df = df[df["Title"].str.contains(search, case=False)]
    st.dataframe(df.style.hide(axis='index'), use_container_width=True)

# --- User Login ---
elif menu == "Login":
    st.title("🔑 User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.current_user = username
            st.success(f"✅ Welcome, {username}!")
        else:
            st.error("❌ Invalid credentials.")

# --- Buy a Book ---
elif menu == "Buy a Book":
    if not st.session_state.current_user:
        st.warning("🔒 Please login first from the 'Login' tab.")
    else:
        st.title("🛒 Purchase a Book")
        df = get_books_df()
        book_choice = st.selectbox("Choose a book:", df["Title"])
        index = st.session_state.titles.index(book_choice)

        if st.session_state.stocks[index] <= 0:
            st.error("⚠️ This book is out of stock.")
        else:
            if st.button("Buy Now"):
                st.session_state.stocks[index] -= 1
                sale = {
                    "Customer": st.session_state.current_user,
                    "Book": book_choice,
                    "Price": st.session_state.prices[index],
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.sales.append(sale)
                st.success(f"✅ Purchase successful! You bought '{book_choice}' for Rs.{sale['Price']}")
                receipt_df = pd.DataFrame([sale])
                st.download_button("📄 Download Receipt", receipt_df.to_csv(index=False).encode(),
                                   file_name="receipt.csv", mime="text/csv")

# --- Admin Panel ---
elif menu == "Admin Panel":
    st.title("🔐 Admin Panel")
    if not st.session_state.logged_in_admin:
        user = st.text_input("Admin Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login as Admin"):
            if user == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
                st.session_state.logged_in_admin = True
                st.success("✅ Admin logged in.")
            else:
                st.error("❌ Incorrect admin credentials.")

    if st.session_state.logged_in_admin:
        st.subheader("➕ Add New Book")
        new_title = st.text_input("Book Title")
        new_stock = st.number_input("Stock", min_value=1, step=1)
        new_price = st.number_input("Price (Rs.)", min_value=1, step=1)
        if st.button("Add Book"):
            if new_title:
                new_id = max(st.session_state.book_ids) + 1
                st.session_state.book_ids.append(new_id)
                st.session_state.titles.append(new_title)
                st.session_state.stocks.append(int(new_stock))
                st.session_state.prices.append(int(new_price))
                st.success(f"✅ Book '{new_title}' added.")

        st.subheader("📊 Sales History")
        if st.session_state.sales:
            sales_df = pd.DataFrame(st.session_state.sales)
            st.dataframe(sales_df, use_container_width=True)
            st.download_button("⬇️ Download Sales", sales_df.to_csv(index=False).encode(),
                               file_name="sales.csv", mime="text/csv")
        else:
            st.info("No sales yet.")

        st.subheader("🗑️ Delete Book")
        del_title = st.selectbox("Select Book to Delete", st.session_state.titles)
        if st.button("Delete Book"):
            del_index = st.session_state.titles.index(del_title)
            for key in ["book_ids", "titles", "stocks", "prices"]:
                st.session_state[key].pop(del_index)
            st.success(f"Book '{del_title}' deleted.")
