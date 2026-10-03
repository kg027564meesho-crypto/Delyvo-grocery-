from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
/* =========================================================
   DELYVO SHOP - FINAL PRODUCT + STOCK MANAGEMENT
   ========================================================= */

window.finalShopProducts = [];

window.loadFinalShopProducts = async function () {
  try {
    const token = localStorage.getItem("delyvo_shop_token");

    if (!token) {
      return;
    }

    const headers = {
      apikey: SHOP_SUPABASE_KEY,
      Authorization: `Bearer ${token}`
    };

    const [productsResponse, variantsResponse, inventoryResponse] =
      await Promise.all([
        fetch(
          `${SHOP_SUPABASE_URL}/rest/v1/products?select=id,name,slug,is_active`,
          { headers }
        ),

        fetch(
          `${SHOP_SUPABASE_URL}/rest/v1/product_variants?select=id,product_id,name,sku,mrp,selling_price,is_active,quantity_value,quantity_unit&order=name.asc`,
          { headers }
        ),

        fetch(
          `${SHOP_SUPABASE_URL}/rest/v1/inventory?select=id,product_id,variant_id,stock_qty,reserved_qty,reorder_level&store_id=eq.7ef989c8-9826-437b-8a63-bb0dfa817540`,
          { headers }
        )
      ]);

    const products = await productsResponse.json();
    const variants = await variantsResponse.json();
    const inventory = await inventoryResponse.json();

    if (!productsResponse.ok) {
      throw new Error("Products load nahi hue.");
    }

    if (!variantsResponse.ok) {
      throw new Error("Product variants load nahi hue.");
    }

    if (!inventoryResponse.ok) {
      throw new Error("Inventory load nahi hua.");
    }

    const productMap = {};

    products.forEach(product => {
      productMap[product.id] = product;
    });

    const inventoryMap = {};

    inventory.forEach(row => {
      inventoryMap[row.variant_id] = row;
    });

    window.finalShopProducts = variants.map(variant => {
      const product = productMap[variant.product_id] || {};
      const stock = inventoryMap[variant.id] || {};

      return {
        id: variant.id,
        product_id: variant.product_id,
        name: product.name || "Product",
        variant_name: variant.name || "",
        sku: variant.sku || "",
        mrp: Number(variant.mrp || 0),
        selling_price: Number(variant.selling_price || 0),
        is_active: variant.is_active !== false,
        stock_qty: Number(stock.stock_qty || 0),
        reserved_qty: Number(stock.reserved_qty || 0),
        reorder_level: Number(stock.reorder_level || 5),
        inventory_id: stock.id || null,
        quantity_value: variant.quantity_value,
        quantity_unit: variant.quantity_unit
      };
    });

    window.renderFinalShopProducts();

  } catch (error) {
    console.error("PRODUCT LOAD ERROR:", error);
  }
};


/* ---------------------------------------------------------
   PRODUCT RENDER
   --------------------------------------------------------- */

window.renderFinalShopProducts = function () {
  const section =
    document.getElementById("productsSection") ||
    document.getElementById("shopProductsSection");

  if (!section) return;

  let container =
    document.getElementById("finalShopProductsList");

  if (!container) {
    container = document.createElement("div");
    container.id = "finalShopProductsList";
    section.appendChild(container);
  }

  if (!window.finalShopProducts.length) {
    container.innerHTML = `
      <div class="shop-product-empty">
        No products found.
      </div>
    `;
    return;
  }

  container.innerHTML =
    window.finalShopProducts.map(product => {

      const available =
        product.stock_qty - product.reserved_qty;

      const lowStock =
        available <= product.reorder_level;

      const inactive =
        !product.is_active;

      const statusText =
        inactive
          ? "Inactive"
          : lowStock
            ? "Low Stock"
            : "Active";

      const statusClass =
        inactive
          ? "inactive"
          : lowStock
            ? "low"
            : "active";

      return `
        <div
          class="final-shop-product"
          data-product-id="${product.id}"
          data-name="${escapeShopText(
            product.name + " " + product.variant_name
          ).toLowerCase()}"
          data-status="${statusClass}"
        >

          <div class="final-product-main">

            <div class="final-product-info">
              <strong>
                ${escapeShopText(product.name)}
              </strong>

              ${
                product.variant_name
                  ? `<span>
                      ${escapeShopText(product.variant_name)}
                    </span>`
                  : ""
              }

              ${
                product.sku
                  ? `<small>
                      SKU: ${escapeShopText(product.sku)}
                    </small>`
                  : ""
              }
            </div>

            <span class="final-product-status ${statusClass}">
              ${statusText}
            </span>

          </div>


          <div class="final-product-fields">

            <label>
              MRP
              <input
                type="number"
                step="0.01"
                min="0"
                data-field="mrp"
                value="${product.mrp}"
              >
            </label>

            <label>
              Selling Price
              <input
                type="number"
                step="0.01"
                min="0"
                data-field="selling_price"
                value="${product.selling_price}"
              >
            </label>

            <label>
              Stock
              <input
                type="number"
                step="1"
                min="0"
                data-field="stock_qty"
                value="${product.stock_qty}"
              >
            </label>

          </div>


          <div class="final-product-bottom">

            <div>
              Available:
              <strong>
                ${available}
              </strong>

              ${
                lowStock
                  ? `<span class="final-low-stock">
                      Low stock
                    </span>`
                  : ""
              }
            </div>

            <div class="final-product-buttons">

              <button
                class="secondary-btn"
                onclick="toggleFinalShopProduct('${product.id}')"
              >
                ${product.is_active ? "Turn Off" : "Turn On"}
              </button>

              <button
                class="primary-btn"
                onclick="saveFinalShopProduct('${product.id}')"
              >
                Save
              </button>

            </div>

          </div>

        </div>
      `;
    }).join("");
};


/* ---------------------------------------------------------
   SAVE PRODUCT
   --------------------------------------------------------- */

window.saveFinalShopProduct = async function (variantId) {
  try {
    const token =
      localStorage.getItem("delyvo_shop_token");

    const card =
      document.querySelector(
        `.final-shop-product[data-product-id="${variantId}"]`
      );

    if (!card) return;

    const product =
      window.finalShopProducts.find(
        item => item.id === variantId
      );

    if (!product) return;

    const mrp =
      Number(
        card.querySelector(
          '[data-field="mrp"]'
        ).value
      );

    const sellingPrice =
      Number(
        card.querySelector(
          '[data-field="selling_price"]'
        ).value
      );

    const stock =
      Number(
        card.querySelector(
          '[data-field="stock_qty"]'
        ).value
      );

    if (mrp < 0 || sellingPrice < 0 || stock < 0) {
      alert("Price aur stock 0 se kam nahi ho sakta.");
      return;
    }

    if (sellingPrice > mrp) {
      alert("Selling price MRP se zyada nahi ho sakta.");
      return;
    }

    const headers = {
      "Content-Type": "application/json",
      apikey: SHOP_SUPABASE_KEY,
      Authorization: `Bearer ${token}`,
      Prefer: "return=minimal"
    };

    const variantResponse =
      await fetch(
        `${SHOP_SUPABASE_URL}/rest/v1/product_variants?id=eq.${variantId}`,
        {
          method: "PATCH",
          headers,
          body: JSON.stringify({
            mrp: mrp,
            selling_price: sellingPrice
          })
        }
      );

    if (!variantResponse.ok) {
      const error = await variantResponse.text();
      throw new Error(error || "Product price save failed.");
    }

    if (product.inventory_id) {
      const inventoryResponse =
        await fetch(
          `${SHOP_SUPABASE_URL}/rest/v1/inventory?id=eq.${product.inventory_id}`,
          {
            method: "PATCH",
            headers,
            body: JSON.stringify({
              stock_qty: stock,
              updated_at: new Date().toISOString()
            })
          }
        );

      if (!inventoryResponse.ok) {
        const error = await inventoryResponse.text();
        throw new Error(
          error || "Inventory save failed."
        );
      }
    }

    alert("Product updated successfully.");

    await window.loadFinalShopProducts();

    if (typeof window.loadShopDashboard === "function") {
      await window.loadShopDashboard();
    }

  } catch (error) {
    console.error(error);
    alert(error.message || "Product update failed.");
  }
};


/* ---------------------------------------------------------
   ACTIVE / INACTIVE
   --------------------------------------------------------- */

window.toggleFinalShopProduct = async function (variantId) {
  try {
    const token =
      localStorage.getItem("delyvo_shop_token");

    const product =
      window.finalShopProducts.find(
        item => item.id === variantId
      );

    if (!product) return;

    const newState =
      !product.is_active;

    const response =
      await fetch(
        `${SHOP_SUPABASE_URL}/rest/v1/product_variants?id=eq.${variantId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            apikey: SHOP_SUPABASE_KEY,
            Authorization: `Bearer ${token}`,
            Prefer: "return=minimal"
          },
          body: JSON.stringify({
            is_active: newState
          })
        }
      );

    if (!response.ok) {
      throw new Error(
        "Product status update failed."
      );
    }

    await window.loadFinalShopProducts();

  } catch (error) {
    console.error(error);
    alert(error.message || "Product status update failed.");
  }
};


/* ---------------------------------------------------------
   SEARCH + FILTER
   --------------------------------------------------------- */

window.filterFinalShopProducts = function () {
  const search =
    String(
      document.getElementById(
        "finalShopProductSearch"
      )?.value || ""
    ).trim().toLowerCase();

  const filter =
    String(
      document.getElementById(
        "finalShopProductFilter"
      )?.value || "all"
    ).toLowerCase();

  document
    .querySelectorAll(".final-shop-product")
    .forEach(card => {

      const name =
        String(
          card.dataset.name || ""
        ).toLowerCase();

      const status =
        String(
          card.dataset.status || ""
        ).toLowerCase();

      const matchesSearch =
        !search ||
        name.includes(search);

      const matchesFilter =
        filter === "all" ||
        status === filter;

      card.style.display =
        matchesSearch && matchesFilter
          ? ""
          : "none";
    });
};


/* ---------------------------------------------------------
   FILTER UI
   --------------------------------------------------------- */

window.addFinalShopProductFilters = function () {
  const section =
    document.getElementById("productsSection") ||
    document.getElementById("shopProductsSection");

  if (!section) return;

  if (
    document.getElementById(
      "finalShopProductFilters"
    )
  ) {
    return;
  }

  const box =
    document.createElement("div");

  box.id =
    "finalShopProductFilters";

  box.className =
    "final-shop-product-filters";

  box.innerHTML = `
    <input
      id="finalShopProductSearch"
      type="search"
      placeholder="Search product..."
    >

    <select id="finalShopProductFilter">
      <option value="all">All Products</option>
      <option value="active">Active</option>
      <option value="inactive">Inactive</option>
      <option value="low">Low Stock</option>
    </select>
  `;

  section.prepend(box);

  document
    .getElementById(
      "finalShopProductSearch"
    )
    .addEventListener(
      "input",
      window.filterFinalShopProducts
    );

  document
    .getElementById(
      "finalShopProductFilter"
    )
    .addEventListener(
      "change",
      window.filterFinalShopProducts
    );
};


/* ---------------------------------------------------------
   STYLE
   --------------------------------------------------------- */

if (
  !document.getElementById(
    "final-shop-products-css"
  )
) {
  const style =
    document.createElement("style");

  style.id =
    "final-shop-products-css";

  style.textContent = `
    .final-shop-product-filters {
      display: flex;
      gap: 10px;
      margin: 16px 0;
      flex-wrap: wrap;
    }

    .final-shop-product-filters input,
    .final-shop-product-filters select {
      padding: 10px 12px;
      border: 1px solid #ddd;
      border-radius: 10px;
      min-height: 42px;
    }

    .final-shop-product {
      border: 1px solid #e5e5e5;
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 12px;
      background: #fff;
    }

    .final-product-main,
    .final-product-bottom,
    .final-product-buttons {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .final-product-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .final-product-info span {
      color: #666;
    }

    .final-product-info small {
      color: #888;
    }

    .final-product-status {
      padding: 5px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }

    .final-product-status.active {
      background: #e8f7ed;
      color: #16803c;
    }

    .final-product-status.low {
      background: #fff4d6;
      color: #9a6b00;
    }

    .final-product-status.inactive {
      background: #eee;
      color: #666;
    }

    .final-product-fields {
      display: grid;
      grid-template-columns:
        repeat(3, minmax(120px, 1fr));
      gap: 12px;
      margin: 16px 0;
    }

    .final-product-fields label {
      display: flex;
      flex-direction: column;
      gap: 5px;
      font-size: 13px;
      color: #555;
    }

    .final-product-fields input {
      padding: 9px;
      border: 1px solid #ddd;
      border-radius: 8px;
    }

    .final-low-stock {
      margin-left: 8px;
      color: #b56d00;
      font-weight: 700;
    }

    .shop-product-empty {
      padding: 30px;
      text-align: center;
    }

    @media (max-width: 650px) {
      .final-product-fields {
        grid-template-columns: 1fr;
      }

      .final-product-main,
      .final-product-bottom {
        align-items: flex-start;
        flex-direction: column;
      }
    }
  `;

  document.head.appendChild(style);
}


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function () {
    setTimeout(function () {
      window.addFinalShopProductFilters();
      window.loadFinalShopProducts();
    }, 700);
  }
);

</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)

print("FINAL SHOP PRODUCTS + STOCK MANAGEMENT ADDED")
