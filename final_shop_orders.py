from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
/* =========================================================
   DELYVO SHOP PANEL - FINAL ORDER MANAGEMENT
   ========================================================= */

window.renderFinalShopOrders = function(orders) {
  const container =
    document.getElementById("shopOrdersList") ||
    document.getElementById("ordersList") ||
    document.getElementById("shop-orders-list");

  if (!container) return;

  if (!Array.isArray(orders) || !orders.length) {
    container.innerHTML = `
      <div class="shop-order-empty">
        <h3>No Orders</h3>
        <p>Abhi koi customer order nahi hai.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = orders.map(order => {
    const status = String(order.status || "pending").toLowerCase();

    const address = order.addresses || order.address || {};
    const items = Array.isArray(order.order_items)
      ? order.order_items
      : [];

    const itemHtml = items.length
      ? items.map(item => `
          <div class="shop-order-item">
            <span>
              ${escapeShopText(item.product_name || "Product")}
              ${item.variant_name
                ? ` (${escapeShopText(item.variant_name)})`
                : ""}
              × ${Number(item.quantity || 0)}
            </span>
            <strong>₹${Number(item.total || 0).toFixed(2)}</strong>
          </div>
        `).join("")
      : `<div class="shop-order-item">Items unavailable</div>`;

    const customerHtml = `
      <div class="shop-customer-box">
        <strong>${escapeShopText(
          address.recipient_name || "Customer"
        )}</strong>
        ${address.phone
          ? `<div>📞 ${escapeShopText(address.phone)}</div>`
          : ""}
        ${address.address_line1
          ? `<div>📍 ${escapeShopText(address.address_line1)}</div>`
          : ""}
        ${address.address_line2
          ? `<div>${escapeShopText(address.address_line2)}</div>`
          : ""}
        ${address.landmark
          ? `<div>Landmark: ${escapeShopText(address.landmark)}</div>`
          : ""}
        <div>
          ${escapeShopText(address.city || "Modinagar")},
          ${escapeShopText(address.pincode || "201204")}
        </div>
      </div>
    `;

    let action = "";

    if (status === "pending" || status === "placed") {
      action = `
        <button class="primary-btn"
          onclick="updateShopOrderStatus('${order.id}','confirmed')">
          Accept Order
        </button>
        <button class="danger-btn"
          onclick="rejectShopOrder('${order.id}')">
          Reject
        </button>
      `;
    } else if (status === "confirmed") {
      action = `
        <button class="primary-btn"
          onclick="updateShopOrderStatus('${order.id}','packing')">
          Start Packing
        </button>
      `;
    } else if (status === "packing") {
      action = `
        <button class="primary-btn"
          onclick="updateShopOrderStatus('${order.id}','packed')">
          Mark Ready
        </button>
      `;
    } else if (status === "packed") {
      action = `
        <button class="primary-btn"
          onclick="updateShopOrderStatus('${order.id}','out_for_delivery')">
          Send for Delivery
        </button>
      `;
    } else if (status === "out_for_delivery") {
      action = `
        <button class="primary-btn"
          onclick="markShopOrderDelivered('${order.id}')">
          Mark Delivered
        </button>
      `;
    } else if (status === "delivered") {
      action = `
        <span class="shop-complete-label">
          ✓ Delivered
        </span>
      `;
    } else if (status === "cancelled") {
      action = `
        <span class="shop-cancelled-label">
          Cancelled
        </span>
      `;
    }

    return `
      <article
        class="shop-order-card"
        data-status="${escapeShopText(status)}"
        data-order-number="${escapeShopText(order.order_number || "")}"
      >

        <div class="shop-order-top">
          <div>
            <div class="shop-order-number">
              ${escapeShopText(order.order_number || "Order")}
            </div>
            <div class="shop-order-date">
              ${formatShopDate(order.created_at)}
            </div>
          </div>

          <span class="shop-order-status status-${escapeShopText(status)}">
            ${formatShopStatus(status)}
          </span>
        </div>

        ${customerHtml}

        <div class="shop-order-items">
          ${itemHtml}
        </div>

        <div class="shop-order-total">
          <span>Total</span>
          <strong>₹${Number(order.total || 0).toFixed(2)}</strong>
        </div>

        <div class="shop-order-payment">
          Payment:
          <strong>COD</strong>
        </div>

        <div class="shop-order-actions">
          ${action}
        </div>
      </article>
    `;
  }).join("");
};


window.escapeShopText = function(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};


window.formatShopDate = function(value) {
  if (!value) return "";

  try {
    return new Date(value).toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch (_) {
    return "";
  }
};


window.formatShopStatus = function(status) {
  const map = {
    pending: "New Order",
    placed: "New Order",
    confirmed: "Confirmed",
    packing: "Packing",
    packed: "Ready",
    out_for_delivery: "Out for Delivery",
    delivered: "Delivered",
    cancelled: "Cancelled"
  };

  return map[status] || status;
};


/* ---------------------------------------------------------
   FINAL SEARCH + STATUS FILTER
   --------------------------------------------------------- */

window.filterFinalShopOrders = function() {
  const searchEl =
    document.getElementById("shopOrderSearch");

  const statusEl =
    document.getElementById("shopOrderStatusFilter");

  const search = String(
    searchEl?.value || ""
  ).trim().toLowerCase();

  const status = String(
    statusEl?.value || "all"
  ).toLowerCase();

  document
    .querySelectorAll(".shop-order-card")
    .forEach(card => {
      const number =
        String(card.dataset.orderNumber || "")
          .toLowerCase();

      const text =
        card.textContent.toLowerCase();

      const cardStatus =
        String(card.dataset.status || "")
          .toLowerCase();

      const matchesSearch =
        !search ||
        number.includes(search) ||
        text.includes(search);

      const matchesStatus =
        status === "all" ||
        cardStatus === status;

      card.style.display =
        matchesSearch && matchesStatus
          ? ""
          : "none";
    });
};


/* ---------------------------------------------------------
   FILTER UI
   --------------------------------------------------------- */

window.addFinalShopOrderFilters = function() {
  const section =
    document.getElementById("ordersSection") ||
    document.getElementById("shopOrdersSection");

  if (!section) return;

  if (document.getElementById("finalShopOrderFilters")) {
    return;
  }

  const filters = document.createElement("div");
  filters.id = "finalShopOrderFilters";
  filters.className = "shop-order-filters";

  filters.innerHTML = `
    <input
      id="shopOrderSearch"
      type="search"
      placeholder="Search order or customer..."
    >

    <select id="shopOrderStatusFilter">
      <option value="all">All Orders</option>
      <option value="pending">New</option>
      <option value="confirmed">Confirmed</option>
      <option value="packing">Packing</option>
      <option value="packed">Ready</option>
      <option value="out_for_delivery">
        Out for Delivery
      </option>
      <option value="delivered">Delivered</option>
      <option value="cancelled">Cancelled</option>
    </select>
  `;

  section.prepend(filters);

  document
    .getElementById("shopOrderSearch")
    .addEventListener(
      "input",
      window.filterFinalShopOrders
    );

  document
    .getElementById("shopOrderStatusFilter")
    .addEventListener(
      "change",
      window.filterFinalShopOrders
    );
};


/* ---------------------------------------------------------
   SAFE STATUS UPDATE
   --------------------------------------------------------- */

window.updateShopOrderStatus = async function(
  orderId,
  newStatus
) {
  try {
    if (!orderId || !newStatus) return;

    const token =
      localStorage.getItem("delyvo_shop_token");

    if (!token) {
      alert("Shop login required.");
      return;
    }

    const response = await fetch(
      `${SHOP_SUPABASE_URL}/rest/v1/rpc/transition_order_status`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: SHOP_SUPABASE_KEY,
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          p_order_id: orderId,
          p_new_status: newStatus
        })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.message ||
        data.hint ||
        data.details ||
        "Status update failed."
      );
    }

    if (typeof window.loadShopOrders === "function") {
      await window.loadShopOrders();
    } else if (typeof window.loadOrders === "function") {
      await window.loadOrders();
    } else {
      location.reload();
    }

  } catch (error) {
    console.error(error);
    alert(error.message || "Order status update failed.");
  }
};


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function() {
    setTimeout(
      window.addFinalShopOrderFilters,
      500
    );
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

print("FINAL SHOP ORDER MANAGEMENT ADDED")
