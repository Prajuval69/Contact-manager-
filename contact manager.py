import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="Contact Manager Dashboard",
    page_icon="📇",
    layout="wide",
)

DATA_FILE = "contacts.json"

# ------------------ DATA HANDLING ------------------
def load_contacts():
    """Load contacts from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return pd.DataFrame(json.load(f))
            except json.JSONDecodeError:
                return pd.DataFrame(columns=["Name", "Phone", "Email", "Created On"])
    return pd.DataFrame(columns=["Name", "Phone", "Email", "Created On"])

def save_contacts(df):
    """Save contacts to JSON."""
    df.to_json(DATA_FILE, orient="records", indent=4)

if "contacts" not in st.session_state:
    st.session_state.contacts = load_contacts()

# ------------------ HELPER FUNCTIONS ------------------
def add_contact(name, phone, email):
    """Add a new contact."""
    df = st.session_state.contacts
    if name in df["Name"].values:
        st.warning("⚠️ Contact with this name already exists.")
    else:
        new_contact = pd.DataFrame(
            [[name, phone, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
            columns=["Name", "Phone", "Email", "Created On"]
        )
        st.session_state.contacts = pd.concat([df, new_contact], ignore_index=True)
        save_contacts(st.session_state.contacts)
        st.success("✅ Contact added successfully!")

def edit_contact(old_name, new_name, new_phone, new_email):
    """Edit existing contact."""
    df = st.session_state.contacts
    if old_name in df["Name"].values:
        df.loc[df["Name"] == old_name, ["Name", "Phone", "Email"]] = [new_name, new_phone, new_email]
        save_contacts(df)
        st.session_state.contacts = df
        st.success("✅ Contact updated successfully!")
    else:
        st.error("❌ Contact not found.")

def delete_contact(name):
    """Delete a contact."""
    df = st.session_state.contacts
    if name in df["Name"].values:
        df = df[df["Name"] != name]
        st.session_state.contacts = df
        save_contacts(df)
        st.success("🗑️ Contact deleted successfully!")
    else:
        st.error("❌ Contact not found.")

# ------------------ DASHBOARD HEADER ------------------
st.markdown(
    """
    <h1 style='text-align:center; color:#4B9CD3;'>📇 Contact Manager Dashboard</h1>
    <p style='text-align:center; color:gray;'>Manage, organize, and analyze your contacts with ease — built using Streamlit.</p>
    """,
    unsafe_allow_html=True
)

# ------------------ STATS CARDS ------------------
col1, col2, col3 = st.columns(3)
total_contacts = len(st.session_state.contacts)
unique_emails = st.session_state.contacts["Email"].nunique() if not st.session_state.contacts.empty else 0
latest_added = st.session_state.contacts["Created On"].max() if not st.session_state.contacts.empty else "—"

col1.metric("👥 Total Contacts", total_contacts)
col2.metric("📧 Unique Emails", unique_emails)
col3.metric("🕒 Last Added", latest_added)

st.markdown("---")

# ------------------ SIDEBAR MENU ------------------
menu = [
    "➕ Add Contact",
    "👀 View Contacts",
    "🔍 Search Contact",
    "✏️ Edit Contact",
    "🗑️ Delete Contact",
    "📤 Import / Export"
]
choice = st.sidebar.radio("Menu", menu)

# ------------------ ADD CONTACT ------------------
if choice == "➕ Add Contact":
    st.subheader("Add New Contact")
    with st.form("add_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        submitted = st.form_submit_button("Add Contact")
        if submitted:
            if name and phone and email:
                add_contact(name.strip(), phone.strip(), email.strip())
            else:
                st.error("⚠️ Please fill all fields before submitting.")

# ------------------ VIEW CONTACTS ------------------
elif choice == "👀 View Contacts":
    st.subheader("All Contacts")
    if not st.session_state.contacts.empty:
        sort_by = st.selectbox("Sort By", ["Name", "Phone", "Created On"])
        df_sorted = st.session_state.contacts.sort_values(by=sort_by)
        st.dataframe(df_sorted, use_container_width=True)
    else:
        st.info("No contacts found yet.")

# ------------------ SEARCH CONTACT ------------------
elif choice == "🔍 Search Contact":
    st.subheader("Search Contacts")
    query = st.text_input("Enter name, phone, or email:")
    if query:
        df = st.session_state.contacts
        results = df[df.apply(lambda row: query.lower() in row.astype(str).str.lower().to_string(), axis=1)]
        if not results.empty:
            st.success(f"✅ Found {len(results)} matching contact(s):")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("❌ No matching contact found.")

# ------------------ EDIT CONTACT ------------------
elif choice == "✏️ Edit Contact":
    st.subheader("Edit Contact Details")
    if not st.session_state.contacts.empty:
        selected = st.selectbox("Select contact to edit", st.session_state.contacts["Name"].tolist())
        contact = st.session_state.contacts[st.session_state.contacts["Name"] == selected].iloc[0]
        with st.form("edit_form"):
            new_name = st.text_input("Full Name", contact["Name"])
            new_phone = st.text_input("Phone Number", contact["Phone"])
            new_email = st.text_input("Email Address", contact["Email"])
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                edit_contact(selected, new_name, new_phone, new_email)
    else:
        st.info("No contacts available to edit.")

# ------------------ DELETE CONTACT ------------------
elif choice == "🗑️ Delete Contact":
    st.subheader("Delete Contact")
    if not st.session_state.contacts.empty:
        selected = st.selectbox("Select contact to delete", st.session_state.contacts["Name"].tolist())
        if st.button("Confirm Delete", type="primary"):
            delete_contact(selected)
    else:
        st.info("No contacts available to delete.")

# ------------------ IMPORT / EXPORT ------------------
elif choice == "📤 Import / Export":
    st.subheader("Import / Export Contacts")

    # Export CSV
    st.download_button(
        label="⬇️ Download Contacts as CSV",
        data=st.session_state.contacts.to_csv(index=False).encode("utf-8"),
        file_name="contacts_export.csv",
        mime="text/csv",
    )

    # Import CSV
    uploaded_file = st.file_uploader("📁 Upload a CSV file to import contacts", type=["csv"])
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        st.session_state.contacts = (
            pd.concat([st.session_state.contacts, new_df], ignore_index=True)
            .drop_duplicates(subset="Name")
            .reset_index(drop=True)
        )
        save_contacts(st.session_state.contacts)
        st.success(f"📥 Imported {len(new_df)} contacts successfully!")
