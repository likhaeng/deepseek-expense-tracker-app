import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def shorten_label(label, max_length=20):
    """
    Shortens long category descriptions to improve readability.
    """
    return label if len(label) <= max_length else label[:max_length] + "..."

def plot_spending_chart(df):

    # Ensure DataFrame is not empty
    if df.empty:
        st.warning("No transactions available for visualization.")
        return

    # ✅ Apply Dark Theme
    # plt.style.use("dark_background")
    # sns.set_palette("magma")  # Use a dark-friendly color palette
    # sns.set_style("dark")

    # 1️⃣ **Category-wise Spending Breakdown (Improved Bar Chart)**
    st.subheader("📊 Spending by Creditor")
    category_spending = df.groupby("CreditorName")["Total"].sum().sort_values(ascending=False)

    if not category_spending.empty:
        top_categories = category_spending[:10]  # Show only top 10 spending categories
        category_labels = [shorten_label(label) for label in top_categories.index]  # Apply label shortening

        fig, ax = plt.subplots(figsize=(5, 2.5))  # Adjust size for readability
        sns.barplot(x=top_categories.values, y=category_labels, ax=ax, palette="coolwarm")
        
        ax.set_xlabel("Total Amount (RM)")
        ax.set_ylabel("Creditor")
        ax.set_title("Top 10 Amount Creditors")
        ax.tick_params()

        st.pyplot(fig)
    else:
        st.warning("No expense data available for category breakdown.")

    # 2️⃣ **Income vs Expense Comparison (Bar Chart)**
    # st.subheader("💰 Income vs Expense")
    # income_expense = df.groupby("transaction_type")["amount"].sum()

    # if not income_expense.empty:
    #     fig, ax = plt.subplots(figsize=(5, 2.5))
    #     income_expense.plot(kind="bar", color=["green", "red"], ax=ax)

    #     ax.set_ylabel("Total Amount (₹)", color="white")
    #     ax.set_title("Income vs Expenses", color="white")
    #     ax.set_xticklabels(["Expense", "Income"], rotation=0, color="white")
    #     ax.tick_params(colors="white")

    #     st.pyplot(fig)
    # else:
    #     st.warning("No sufficient data for income vs expense comparison.")
