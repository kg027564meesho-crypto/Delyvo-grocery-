from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";
  const STORE_ID = "7ef989c8-9826-437b-8a63-bb0dfa817540";

  function token() {
    return localStorage.getItem("delyvo_shop_token") || "";
  }

  async function api(path, options = {}) {
    const headers = {
      apikey: KEY,
      Authorization: "Bearer " + token(),
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const r = await fetch(URL + path, {...options, headers});
    const data = await r.json().catch(() => null);

    if (!r.ok) {
      throw new Error(data?.message || data?.msg || "Request failed");
    }
    return data;
  }

  async function loadProducts() {
    const box = document.getElementById("delyvoProductsBox");
    if (!box) return;

    box.innerHTML = "<p>Products loading...</p>";

    try {
      const products = await api(
        "/rest/v1/products?select=id,name,slug,mrp,selling_price,is_active&order=name.asc"
      );

      const variants = await api(
        "/rest/v1/product_variants?select=id,product_id,name,mrp,selling_price,is_active&order=name.asc"
      );

      const inventory = await api(
        "/rest/v1/inventory?select=id,product_id,variant_id,stock_qty,reserved_qty,reorder_level&store_id=eq." +
        STORE_ID
      );

      const vmap = {};
      variants.forEach(v => vmap[v.product_id] = v);

      const imap = {};
      inventory.forEach(i => imap[i.variant_id] = i);

      box.innerHTML = "";

      if (!products.length) {
        box.innerHTML = "<p>No products found.</p>";
        return;
      }

      products.forEach(product => {
        const v = vmap[product.id];
        if (!v) return;

        const inv = imap[v.id] || {
          id: "",
          stock_qty: 0,
          reserved_qty: 0,
          reorder_level: 5
        };

        const row = document.createElement("div");
        row.className = "delyvo-product-row";

        row.innerHTML = `
          <div class="dp-name">
            <strong>${escapeHtml(product.name)}</strong>
            <small>${escapeHtml(v.name || "")}</small>
          </div>

          <input class="dp-input"
            type="number"
            min="0"
            step="0.01"
            value="${Number(v.mrp || 0)}"
            data-mrp>

          <input class="dp-input"
            type="number"
            min="0"
            step="0.01"
            value="${Number(v.selling_price || 0)}"
            data-price>

          <input class="dp-input"
            type="number"
            min="0"
            step="1"
            value="${Number(inv.stock_qty || 0)}"
            data-stock>

          <button class="dp-save">Save</button>
        `;

        row.querySelector(".dp-save").onclick = async () => {
          const btn = row.querySelector(".dp-save");
          const mrp = Number(row.querySelector("[data-mrp]").value);
          const price = Number(row.querySelector("[data-price]").value);
          const stock = Number(row.querySelector("[data-stock]").value);

          if (price < 0 || mrp < 0 || stock < 0) {
            alert("Value 0 se kam nahi ho sakti.");
            return;
          }

          btn.disabled = true;
          btn.textContent = "Saving...";

          try {
            await api(
              "/rest/v1/product_variants?id=eq." + v.id,
              {
                method: "PATCH",
                headers: {"Prefer": "return=minimal"},
                body: JSON.stringify({
                  mrp: mrp,
                  selling_price: price
                })
              }
            );

            if (inv.id) {
              await api(
                "/rest/v1/inventory?id=eq." + inv.id,
                {
                  method: "PATCH",
                  headers: {"Prefer": "return=minimal"},
                  body: JSON.stringify({
                    stock_qty: stock
                  })
                }
              );
            }

            btn.textContent = "Saved ✓";
            setTimeout(() => btn.textContent = "Save", 1200);

          } catch (e) {
            alert(e.message);
            btn.textContent = "Save";
          } finally {
            btn.disabled = false;
          }
        };

        box.appendChild(row);
      });

    } catch (e) {
      box.innerHTML =
        "<p style='color:#b00020'>Products load nahi hue: " +
        escapeHtml(e.message) + "</p>";
    }
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function addPanel() {
    if (document.getElementById("delyvoProductsPanel")) return;

    const panel = document.createElement("section");
    panel.id = "delyvoProductsPanel";
    panel.innerHTML = `
      <div class="dp-head">
        <div>
          <h2>Products & Stock</h2>
          <p>Price aur stock yahin se manage karo.</p>
        </div>
        <button id="dpRefresh">Refresh</button>
      </div>

      <div class="dp-table-head">
        <span>Product</span>
        <span>MRP</span>
        <span>Selling Price</span>
        <span>Stock</span>
        <span>Action</span>
      </div>

      <div id="delyvoProductsBox"></div>
    `;

    document.body.appendChild(panel);

    document.getElementById("dpRefresh").onclick = loadProducts;
  }

  function addStyle() {
    const style = document.createElement("style");
    style.textContent = `
      #delyvoProductsPanel {
        margin: 24px auto;
        max-width: 1100px;
        padding: 20px;
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,.08);
      }

      .dp-head {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:15px;
        margin-bottom:18px;
      }

      .dp-head h2 {
        margin:0 0 5px;
      }

      .dp-head p {
        margin:0;
        color:#666;
      }

      #dpRefresh {
        border:0;
        padding:10px 16px;
        border-radius:9px;
        cursor:pointer;
        background:#111;
        color:#fff;
      }

      .dp-table-head,
      .delyvo-product-row {
        display:grid;
        grid-template-columns: 2fr 1fr 1.2fr 1fr 90px;
        gap:10px;
        align-items:center;
      }

      .dp-table-head {
        padding:10px;
        font-weight:700;
        background:#f5f5f5;
        border-radius:8px;
      }

      .delyvo-product-row {
        padding:12px 10px;
        border-bottom:1px solid #eee;
      }

      .dp-name strong,
      .dp-name small {
        display:block;
      }

      .dp-name small {
        color:#777;
        margin-top:3px;
      }

      .dp-input {
        width:100%;
        box-sizing:border-box;
        padding:9px;
        border:1px solid #ddd;
        border-radius:8px;
      }

      .dp-save {
        border:0;
        border-radius:8px;
        padding:9px 12px;
        background:#111;
        color:#fff;
        cursor:pointer;
      }

      .dp-save:disabled {
        opacity:.6;
        cursor:wait;
      }

      @media(max-width:700px) {
        .dp-table-head {
          display:none;
        }

        .delyvo-product-row {
          grid-template-columns:1fr 1fr;
          padding:16px 5px;
        }

        .dp-name {
          grid-column:1 / -1;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function start() {
    addStyle();
    addPanel();

    if (token()) {
      loadProducts();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("SHOP PRODUCTS + PRICE + STOCK PANEL ADDED")
