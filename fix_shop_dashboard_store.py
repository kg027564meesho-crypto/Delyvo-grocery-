from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

STORE_ID = "7ef989c8-9826-437b-8a63-bb0dfa817540"

old = "/rest/v1/inventory?select=id,stock_qty,reorder_level"
new = "/rest/v1/inventory?select=id,stock_qty,reorder_level&store_id=eq." + STORE_ID

count = html.count(old)
html = html.replace(old, new)

p.write_text(html)

print("SHOP DASHBOARD MODINAGAR STORE FILTER FIXED")
print("REPLACED:", count)
