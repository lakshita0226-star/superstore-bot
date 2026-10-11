import sqlite3, os
import pandas as pd

DB = "superstore.db"
if os.path.exists(DB):
    os.remove(DB)

con = sqlite3.connect(DB)

files = {
    "customers": "Customers.csv",
    "products": "Products.csv",
    "orders": "Orders.csv",
    "order_details": "Order_Details.csv",
}

for table, f in files.items():
    df = pd.read_csv(f"data/{f}", encoding="utf-8")
    df.columns = [c.strip().replace("-", "_").replace(" ", "_") for c in df.columns]
    df.to_sql(table, con, index=False)
    print(table, df.shape, list(df.columns))

con.executescript("""
CREATE UNIQUE INDEX ix_cust   ON customers(Customer_ID);
CREATE UNIQUE INDEX ix_prod   ON products(Product_ID);
CREATE UNIQUE INDEX ix_ord    ON orders(Order_Key);
CREATE UNIQUE INDEX ix_od     ON order_details(Order_Key, Product_ID);
CREATE INDEX ix_od_prod       ON order_details(Product_ID);
CREATE INDEX ix_ord_cust      ON orders(Customer_ID);
CREATE INDEX ix_ord_date      ON orders(Order_Date);
""")

# sanity check
print(con.execute("""
SELECT COUNT(*), SUM(od.Sales), SUM(od.Profit),
       COUNT(DISTINCT o.Order_ID), COUNT(DISTINCT o.Order_Key)
FROM order_details od
JOIN orders o    ON o.Order_Key = od.Order_Key
JOIN customers c ON c.Customer_ID = o.Customer_ID
JOIN products p  ON p.Product_ID = od.Product_ID
""").fetchone())
con.commit()
con.close()