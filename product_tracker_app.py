# Streamlit Web App: Amazon & Noon Product Tracker
# ---------------------------------------------------
# Requirements: streamlit, requests, beautifulsoup4, pandas

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Product Tracker", layout="wide")
st.title("Amazon & Noon Product Tracker")

# --- User Input ---
platform = st.selectbox("Select Platform", ["Amazon.ae", "Noon.com"])
search_query = st.text_input("Enter Product Name or Category")
search_button = st.button("Search")

# --- Helper Functions ---
def get_amazon_data(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f"https://www.amazon.ae/s?k={query.replace(' ', '+')}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch Amazon data: {e}")
        return []

    soup = BeautifulSoup(res.content, "html.parser")
    products = []
    for item in soup.select(".s-result-item"):
        title = item.select_one("h2 span")
        price = item.select_one(".a-price-whole")
        seller = "Amazon"
        rating = item.select_one(".a-icon-alt")
        reviews = item.select_one(".a-size-base.s-underline-text")

        if title and price:
            products.append({
                "Title": title.get_text().strip(),
                "Price (AED)": price.get_text().strip(),
                "Seller": seller,
                "Rating": rating.get_text().strip() if rating else "-",
                "Reviews": reviews.get_text().strip() if reviews else "-",
                "Sold": "-"
            })
    return products

def get_noon_data(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f"https://www.noon.com/uae-en/search/?q={query.replace(' ', '+')}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch Noon data: {e}")
        return []

    soup = BeautifulSoup(res.content, "html.parser")
    products = []
    for item in soup.select(".productContainer"):
        title = item.select_one(".name")
        price = item.select_one(".priceNow")
        seller = item.select_one(".storeName")

        if title and price:
            products.append({
                "Title": title.get_text().strip(),
                "Price (AED)": price.get_text().strip(),
                "Seller": seller.get_text().strip() if seller else "Noon",
                "Rating": "-",
                "Reviews": "-",
                "Sold": "-"
            })
    return products

# --- Main Logic ---
if search_button and search_query:
    with st.spinner("Fetching product data..."):
        if platform == "Amazon.ae":
            data = get_amazon_data(search_query)
        else:
            data = get_noon_data(search_query)

        if data:
            df = pd.DataFrame(data)
            st.success(f"Showing results for '{search_query}' on {platform}:")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No products found or unable to fetch data.")
