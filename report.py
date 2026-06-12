"""Monthly spending summary from the scanned receipts.

    python report.py
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    df = pd.read_csv("output/expenses.csv")
    df = df.dropna(subset=["total"])

    print(f"\n{len(df)} receipts, {df['total'].sum():.2f} EUR total\n")
    by_cat = df.groupby("category")["total"].agg(["sum", "count"]).sort_values("sum", ascending=False)
    for cat, row in by_cat.iterrows():
        print(f"  {cat:<12} {row['sum']:>8.2f} EUR  ({int(row['count'])} receipts)")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(by_cat["sum"], labels=by_cat.index, autopct="%1.0f%%",
           startangle=90, counterclock=False)
    ax.set_title("Spending by category")
    fig.tight_layout()
    fig.savefig("output/spending.png", dpi=120)
    print("\nChart saved to output/spending.png")


if __name__ == "__main__":
    main()
