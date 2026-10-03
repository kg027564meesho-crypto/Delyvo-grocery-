from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
/* =========================================================
   DELYVO SHOP - FINAL DASHBOARD
   ========================================================= */

window.loadFinalShopDashboard = async function () {
  try {
    const token = localStorage.getItem("delyvo_shop_token");

    if (!token) return;

    const headers = {
      apikey: SHOP_SUPABASE_KEY,
      Authorization: `Bearer ${token}`
    };

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const todayISO = today.toISOString();

    const [
      ordersResponse,
      productsResponse,
      inventoryResponse
    ] = await Promise.all([
      fetch(
        `${SHOP_SUPABASE_URL}/rest/v1/orders?select=id,status,total,created_at&created_at=gte.${encodeURIComponent(todayISO)}&order=created_at.desc`,
        { headers }
      ),

      fetch(
        `${SHOP_SUPABASE_URL}/rest/v1/product_variants?select=id,is_active`,
        { headers }
      ),

      fetch(
        `${SHOP_SUPABASE_URL}/rest/v1/inventory?select=id,stock_qty,reserved_qty,reorder_level&store_id=eq.7ef989c8-9826-437b-8a63-bb0dfa817540`,
        { headers }
      )
    ]);

    const orders = await ordersResponse.json();
    const products = await productsResponse.json();
    const inventory = await inventoryResponse.json();

    if (!ordersResponse.ok) {
      throw new Error("Orders dashboard load failed.");
    }

    if (!productsResponse.ok) {
      throw new Error("Products dashboard load failed.");
    }

    if (!inventoryResponse.ok) {
      throw new Error("Inventory dashboard load failed.");
    }

    const safeOrders =
      Array.isArray(orders) ? orders : [];

    const safeProducts =
      Array.isArray(products) ? products : [];

    const safeInventory =
      Array.isArray(inventory) ? inventory : [];

    const totalOrders =
      safeOrders.length;

    const pendingOrders =
      safeOrders.filter(order =>
        ["pending", "placed"].includes(
          String(order.status || "").toLowerCase()
        )
      ).length;

    const preparingOrders =
      safeOrders.filter(order =>
        ["confirmed", "packing", "packed"].includes(
          String(order.status || "").toLowerCase()
        )
      ).length;

    const outForDeliveryOrders =
      safeOrders.filter(order =>
        String(order.status || "").toLowerCase() ===
        "out_for_delivery"
      ).length;

    const deliveredOrders =
      safeOrders.filter(order =>
        String(order.status || "").toLowerCase() ===
        "delivered"
      ).length;

    const todaySales =
      safeOrders
        .filter(order =>
          String(order.status || "").toLowerCase() !==
          "cancelled"
        )
        .reduce(
          (sum, order) =>
            sum + Number(order.total || 0),
          0
        );

    const lowStock =
      safeInventory.filter(item => {
        const available =
          Number(item.stock_qty || 0) -
          Number(item.reserved_qty || 0);

        return available <=
          Number(item.reorder_level || 5);
      }).length;

    const activeProducts =
      safeProducts.filter(
        product => product.is_active !== false
      ).length;

    const setValue = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };

    setValue("finalDashOrders", totalOrders);
    setValue("finalDashPending", pendingOrders);
    setValue("finalDashPreparing", preparingOrders);
    setValue("finalDashDelivery", outForDeliveryOrders);
    setValue(
      "finalDashSales",
      `₹${todaySales.toFixed(2)}`
    );
    setValue("finalDashLowStock", lowStock);
    setValue("finalDashProducts", activeProducts);
    setValue(
      "finalDashDelivered",
      deliveredOrders
    );

    const updated =
      document.getElementById(
        "finalDashUpdated"
      );

    if (updated) {
      updated.textContent =
        `Updated ${new Date().toLocaleTimeString(
          "en-IN",
          {
            hour: "2-digit",
            minute: "2-digit"
          }
        )}`;
    }

  } catch (error) {
    console.error(
      "FINAL DASHBOARD ERROR:",
      error
    );
  }
};


/* ---------------------------------------------------------
   DASHBOARD UI
   --------------------------------------------------------- */

window.addFinalShopDashboard = function () {

  if (
    document.getElementById(
      "finalShopDashboard"
    )
  ) {
    return;
  }

  const dashboard =
    document.createElement("section");

  dashboard.id =
    "finalShopDashboard";

  dashboard.className =
    "final-shop-dashboard";

  dashboard.innerHTML = `
    <div class="final-dashboard-header">

      <div>
        <h2>Shop Dashboard</h2>
        <p>Delyvo Modinagar Store</p>
      </div>

      <div class="final-dashboard-actions">

        <span id="finalDashUpdated">
          Loading...
        </span>

        <button
          class="secondary-btn"
          onclick="loadFinalShopDashboard()"
        >
          Refresh
        </button>

      </div>

    </div>


    <div class="final-dashboard-grid">

      <div class="final-dashboard-card">
        <span>Today's Orders</span>
        <strong id="finalDashOrders">0</strong>
      </div>

      <div class="final-dashboard-card">
        <span>Pending</span>
        <strong id="finalDashPending">0</strong>
      </div>

      <div class="final-dashboard-card">
        <span>Preparing</span>
        <strong id="finalDashPreparing">0</strong>
      </div>

      <div class="final-dashboard-card">
        <span>Out for Delivery</span>
        <strong id="finalDashDelivery">0</strong>
      </div>

      <div class="final-dashboard-card">
        <span>Delivered</span>
        <strong id="finalDashDelivered">0</strong>
      </div>

      <div class="final-dashboard-card">
        <span>Today's Sales</span>
        <strong id="finalDashSales">₹0.00</strong>
      </div>

      <div class="final-dashboard-card">
        <span>Low Stock</span>
        <strong id="finalDashLowStock">0</strong>
      </div>

      <div class="final-dashboard-card">
        <span>Active Products</span>
        <strong id="finalDashProducts">0</strong>
      </div>

    </div>


    <div class="final-dashboard-note">
      Orders automatically refresh every 30 seconds.
    </div>
  `;

  const firstBodyChild =
    document.body.firstElementChild;

  if (firstBodyChild) {
    document.body.insertBefore(
      dashboard,
      firstBodyChild
    );
  } else {
    document.body.appendChild(
      dashboard
    );
  }
};


/* ---------------------------------------------------------
   AUTO REFRESH
   --------------------------------------------------------- */

window.finalShopDashboardInterval =
  window.finalShopDashboardInterval ||
  setInterval(function () {

    if (
      typeof window.loadFinalShopDashboard ===
      "function"
    ) {
      window.loadFinalShopDashboard();
    }

    if (
      typeof window.loadFinalShopProducts ===
      "function"
    ) {
      window.loadFinalShopProducts();
    }

    if (
      typeof window.loadShopOrders ===
      "function"
    ) {
      window.loadShopOrders();
    } else if (
      typeof window.loadOrders ===
      "function"
    ) {
      window.loadOrders();
    }

  }, 30000);


/* ---------------------------------------------------------
   STYLE
   --------------------------------------------------------- */

if (
  !document.getElementById(
    "final-shop-dashboard-css"
  )
) {

  const style =
    document.createElement("style");

  style.id =
    "final-shop-dashboard-css";

  style.textContent = `
    .final-shop-dashboard {
      margin: 20px auto;
      max-width: 1200px;
      padding: 0 16px;
    }

    .final-dashboard-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }

    .final-dashboard-header h2 {
      margin: 0 0 4px;
    }

    .final-dashboard-header p {
      margin: 0;
      color: #777;
    }

    .final-dashboard-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    #finalDashUpdated {
      color: #777;
      font-size: 13px;
    }

    .final-dashboard-grid {
      display: grid;
      grid-template-columns:
        repeat(4, minmax(150px, 1fr));
      gap: 14px;
    }

    .final-dashboard-card {
      border: 1px solid #e5e5e5;
      border-radius: 14px;
      padding: 18px;
      background: #fff;
      min-height: 90px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
    }

    .final-dashboard-card span {
      color: #666;
      font-size: 14px;
    }

    .final-dashboard-card strong {
      font-size: 27px;
    }

    .final-dashboard-note {
      margin-top: 14px;
      color: #777;
      font-size: 13px;
    }

    @media (max-width: 800px) {
      .final-dashboard-grid {
        grid-template-columns:
          repeat(2, minmax(140px, 1fr));
      }

      .final-dashboard-header {
        align-items: flex-start;
        flex-direction: column;
      }
    }

    @media (max-width: 480px) {
      .final-dashboard-grid {
        grid-template-columns: 1fr;
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

      window.addFinalShopDashboard();

      window.loadFinalShopDashboard();

    }, 900);

  }
);

</script>
'''

if "</body>" in html:
    html = html.replace(
        "</body>",
        script + "\n</body>",
        1
    )
else:
    html += script

p.write_text(html)

print("FINAL SHOP DASHBOARD + AUTO REFRESH ADDED")
