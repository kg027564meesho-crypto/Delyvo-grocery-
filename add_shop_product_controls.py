from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

html = html.replace(
'''<span>Stock</span>
        <span>Action</span>''',
'''<span>Stock</span>
        <span>Status</span>
        <span>Action</span>'''
)

html = html.replace(
'''<input class="dp-input"
            type="number"
            min="0"
            step="1"
            value="${Number(inv.stock_qty || 0)}"
            data-stock>

          <button class="dp-save">Save</button>''',
'''<input class="dp-input"
            type="number"
            min="0"
            step="1"
            value="${Number(inv.stock_qty || 0)}"
            data-stock>

          <button class="dp-status ${v.is_active ? "active" : "inactive"}"
            data-status>
            ${v.is_active ? "ON" : "OFF"}
          </button>

          <button class="dp-save">Save</button>'''
)

html = html.replace(
'''grid-template-columns: 2fr 1fr 1.2fr 1fr 90px;''',
'''grid-template-columns: 2fr 1fr 1.2fr 1fr 75px 90px;'''
)

html = html.replace(
'''      .dp-save {
        border:0;''',
'''      .dp-status {
        border:0;
        border-radius:8px;
        padding:9px 8px;
        cursor:pointer;
        font-weight:700;
      }

      .dp-status.active {
        background:#d9f7df;
        color:#08752b;
      }

      .dp-status.inactive {
        background:#eee;
        color:#666;
      }

      .dp-save {
        border:0;'''
)

html = html.replace(
'''          const stock = Number(row.querySelector("[data-stock]").value);

          if (price < 0 || mrp < 0 || stock < 0) {''',
'''          const stock = Number(row.querySelector("[data-stock]").value);
          const activeButton = row.querySelector("[data-status]");
          const isActive = activeButton.dataset.active === "true";

          if (price < 0 || mrp < 0 || stock < 0) {'''
)

html = html.replace(
'''            await api(
              "/rest/v1/product_variants?id=eq." + v.id,
              {
                method: "PATCH",
                headers: {"Prefer": "return=minimal"},
                body: JSON.stringify({
                  mrp: mrp,
                  selling_price: price
                })
              }
            );''',
'''            await api(
              "/rest/v1/product_variants?id=eq." + v.id,
              {
                method: "PATCH",
                headers: {"Prefer": "return=minimal"},
                body: JSON.stringify({
                  mrp: mrp,
                  selling_price: price,
                  is_active: isActive
                })
              }
            );'''
)

marker = '''        row.querySelector(".dp-save").onclick = async () => {'''

insert = '''        const statusButton = row.querySelector("[data-status]");
        statusButton.dataset.active = String(v.is_active);

        statusButton.onclick = () => {
          const current = statusButton.dataset.active === "true";
          const next = !current;

          statusButton.dataset.active = String(next);
          statusButton.textContent = next ? "ON" : "OFF";
          statusButton.classList.toggle("active", next);
          statusButton.classList.toggle("inactive", !next);
        };

        if (Number(inv.stock_qty || 0) <= Number(inv.reorder_level || 5)) {
          row.style.background = "#fff8e1";
          const name = row.querySelector(".dp-name");
          name.insertAdjacentHTML(
            "beforeend",
            '<small style="color:#b36b00;font-weight:700">⚠ Low stock</small>'
          );
        }

'''

html = html.replace(marker, insert + marker)

p.write_text(html)
print("SHOP PRODUCT CONTROLS ADDED")
