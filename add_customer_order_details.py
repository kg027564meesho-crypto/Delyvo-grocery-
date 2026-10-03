from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const DLV_URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const DLV_KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  async function orderApi(path) {
    const token = localStorage.getItem("delyvo_access_token");

    if (!token) {
      throw new Error("Please login first.");
    }

    const response = await fetch(DLV_URL + path, {
      headers: {
        apikey: DLV_KEY,
        Authorization: "Bearer " + token
      }
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(
        data?.message ||
        data?.msg ||
        "Unable to load order"
      );
    }

    return data;
  }

  function statusText(status) {
    const map = {
      placed: "Order Received",
      pending: "Order Received",
      confirmed: "Order Confirmed",
      packing: "Packing",
      packed: "Ready",
      out_for_delivery: "Out for Delivery",
      delivered: "Delivered",
      cancelled: "Cancelled",
      refunded: "Refunded"
    };

    return map[status] || status;
  }

  function statusStep(status) {
    if (status === "placed" || status === "pending") return 1;
    if (status === "confirmed") return 2;
    if (status === "packing") return 3;
    if (status === "packed") return 4;
    if (status === "out_for_delivery") return 5;
    if (status === "delivered") return 6;
    return 0;
  }

  async function openOrderDetails(orderId) {
    let old = document.getElementById("delyvoOrderDetails");
    if (old) old.remove();

    const modal = document.createElement("div");
    modal.id = "delyvoOrderDetails";

    modal.innerHTML = `
      <div class="od-backdrop"></div>

      <div class="od-card">
        <div class="od-head">
          <div>
            <h2>Order Details</h2>
            <p id="odOrderNumber">Loading...</p>
          </div>

          <button class="od-close">×</button>
        </div>

        <div id="odContent">
          <div class="od-loading">Loading order...</div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    modal.querySelector(".od-close").onclick =
      () => modal.remove();

    try {
      const orders = await orderApi(
        "/rest/v1/orders" +
        "?select=id,order_number,status,payment_status,subtotal,delivery_fee,total,created_at,delivered_at,address_id" +
        "&id=eq." + encodeURIComponent(orderId) +
        "&limit=1"
      );

      if (!orders.length) {
        throw new Error("Order not found.");
      }

      const order = orders[0];

      const items = await orderApi(
        "/rest/v1/order_items" +
        "?select=id,product_name,variant_name,quantity,unit_price,total" +
        "&order_id=eq." + encodeURIComponent(orderId) +
        "&order=id"
      );

      document.getElementById("odOrderNumber").textContent =
        order.order_number;

      const current = statusStep(order.status);

      const steps = [
        ["Order Received", 1],
        ["Confirmed", 2],
        ["Packing", 3],
        ["Ready", 4],
        ["Out for Delivery", 5],
        ["Delivered", 6]
      ];

      let timeline = "";

      steps.forEach(([label, step]) => {
        let cls = "";

        if (step < current) cls = "done";
        if (step === current) cls = "active";

        timeline += `
          <div class="od-step ${cls}">
            <div class="od-dot">${step < current ? "✓" : step}</div>
            <span>${label}</span>
          </div>
        `;
      });

      let itemHtml = "";

      items.forEach(item => {
        itemHtml += `
          <div class="od-item">
            <div>
              <strong>${escapeHtml(item.product_name)}</strong>
              ${
                item.variant_name
                ? `<small>${escapeHtml(item.variant_name)}</small>`
                : ""
              }
              <span>Qty: ${Number(item.quantity || 0)}</span>
            </div>

            <strong>
              ₹${Number(item.total || 0).toFixed(0)}
            </strong>
          </div>
        `;
      });

      if (!itemHtml) {
        itemHtml = `<p class="od-muted">No item details available.</p>`;
      }

      document.getElementById("odContent").innerHTML = `
        <div class="od-current">
          <span>Current Status</span>
          <strong>${escapeHtml(statusText(order.status))}</strong>
        </div>

        <div class="od-timeline">
          ${timeline}
        </div>

        <div class="od-section">
          <h3>Items</h3>
          ${itemHtml}
        </div>

        <div class="od-section">
          <h3>Bill Details</h3>

          <div class="od-row">
            <span>Subtotal</span>
            <strong>₹${Number(order.subtotal || 0).toFixed(0)}</strong>
          </div>

          <div class="od-row">
            <span>Delivery Fee</span>
            <strong>₹${Number(order.delivery_fee || 0).toFixed(0)}</strong>
          </div>

          <div class="od-total">
            <span>Total</span>
            <strong>₹${Number(order.total || 0).toFixed(0)}</strong>
          </div>
        </div>

        <div class="od-payment">
          💵 Cash on Delivery
          <span>${escapeHtml(
            String(order.payment_status || "pending").toUpperCase()
          )}</span>
        </div>

        <p class="od-date">
          Ordered: ${formatDate(order.created_at)}
        </p>
      `;

    } catch (error) {
      document.getElementById("odContent").innerHTML = `
        <div class="od-error">
          ${escapeHtml(error.message)}
        </div>
      `;
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

  function formatDate(value) {
    try {
      return new Date(value).toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return "";
    }
  }

  window.openOrderDetails = openOrderDetails;

  const style = document.createElement("style");

  style.textContent = `
    #delyvoOrderDetails {
      position:fixed;
      inset:0;
      z-index:99997;
    }

    .od-backdrop {
      position:absolute;
      inset:0;
      background:rgba(0,0,0,.55);
    }

    .od-card {
      position:relative;
      z-index:2;
      width:min(94%,650px);
      max-height:88vh;
      overflow:auto;
      box-sizing:border-box;
      margin:5vh auto 0;
      padding:22px;
      background:#fff;
      border-radius:20px;
      box-shadow:0 15px 50px rgba(0,0,0,.25);
    }

    .od-head {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:15px;
      margin-bottom:18px;
    }

    .od-head h2 {
      margin:0;
    }

    .od-head p {
      margin:4px 0 0;
      color:#777;
      font-weight:700;
    }

    .od-close {
      width:38px;
      height:38px;
      border:0;
      border-radius:50%;
      background:#f2f2f2;
      font-size:25px;
      cursor:pointer;
    }

    .od-current {
      padding:15px;
      border-radius:13px;
      background:#f5f8ff;
      margin-bottom:18px;
    }

    .od-current span {
      display:block;
      color:#777;
      font-size:12px;
      margin-bottom:5px;
    }

    .od-current strong {
      font-size:18px;
    }

    .od-timeline {
      display:grid;
      grid-template-columns:repeat(6,1fr);
      gap:5px;
      margin:25px 0;
    }

    .od-step {
      text-align:center;
      color:#aaa;
      font-size:10px;
    }

    .od-dot {
      width:30px;
      height:30px;
      margin:0 auto 7px;
      border-radius:50%;
      display:flex;
      justify-content:center;
      align-items:center;
      background:#eee;
      font-weight:800;
    }

    .od-step.done,
    .od-step.active {
      color:#111;
    }

    .od-step.done .od-dot,
    .od-step.active .od-dot {
      background:#111;
      color:#fff;
    }

    .od-section {
      margin-top:20px;
    }

    .od-section h3 {
      margin-bottom:10px;
    }

    .od-item {
      display:flex;
      justify-content:space-between;
      gap:15px;
      padding:12px 0;
      border-bottom:1px solid #eee;
    }

    .od-item small,
    .od-item span {
      display:block;
      color:#777;
      font-size:12px;
      margin-top:3px;
    }

    .od-row,
    .od-total {
      display:flex;
      justify-content:space-between;
      padding:8px 0;
    }

    .od-total {
      border-top:1px solid #eee;
      margin-top:8px;
      padding-top:13px;
      font-size:18px;
    }

    .od-payment {
      margin-top:18px;
      padding:12px;
      border-radius:10px;
      background:#fff7df;
      color:#715500;
      display:flex;
      justify-content:space-between;
      gap:10px;
      font-weight:700;
    }

    .od-date {
      color:#777;
      font-size:12px;
      text-align:center;
      margin-top:15px;
    }

    .od-muted,
    .od-loading,
    .od-error {
      text-align:center;
      padding:25px;
    }

    .od-error {
      color:#b00020;
    }

    @media(max-width:600px) {
      .od-card {
        width:96%;
        margin-top:3vh;
        padding:16px;
      }

      .od-timeline {
        grid-template-columns:repeat(3,1fr);
        row-gap:15px;
      }

      .od-payment {
        flex-direction:column;
      }
    }
  `;

  document.head.appendChild(style);

  // My Orders cards mein View Details button add karna
  const originalOpen = window.openMyOrders;

  if (typeof originalOpen === "function") {
    window.openMyOrders = async function() {
      await originalOpen();

      setTimeout(() => {
        document.querySelectorAll(".mo-order").forEach(card => {
          if (card.querySelector(".mo-view-details")) return;

          const orderNumber =
            card.querySelector(".mo-order-top strong")?.textContent?.trim();

          if (!orderNumber) return;

          const button = document.createElement("button");
          button.className = "mo-view-details";
          button.textContent = "View Details";

          button.onclick = async () => {
            try {
              const orders = await orderApi(
                "/rest/v1/orders" +
                "?select=id,order_number" +
                "&order_number=eq." +
                encodeURIComponent(orderNumber) +
                "&limit=1"
              );

              if (orders.length) {
                openOrderDetails(orders[0].id);
              }
            } catch (error) {
              alert(error.message);
            }
          };

          card.appendChild(button);
        });
      }, 150);
    };
  }

  const extraStyle = document.createElement("style");

  extraStyle.textContent = `
    .mo-view-details {
      width:100%;
      margin-top:12px;
      padding:10px;
      border:1px solid #ddd;
      border-radius:9px;
      background:#fff;
      cursor:pointer;
      font-weight:700;
    }

    .mo-view-details:hover {
      background:#f5f5f5;
    }
  `;

  document.head.appendChild(extraStyle);
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("CUSTOMER ORDER DETAILS + STATUS TRACKING ADDED")
