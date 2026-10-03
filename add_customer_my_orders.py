from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const SUPABASE_URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const SUPABASE_KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  function customerToken() {
    return localStorage.getItem("delyvo_access_token") || "";
  }

  async function customerApi(path) {
    const token = customerToken();

    if (!token) {
      throw new Error("Please login first.");
    }

    const response = await fetch(
      SUPABASE_URL + path,
      {
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: "Bearer " + token
        }
      }
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(
        data?.message ||
        data?.msg ||
        "Unable to load orders"
      );
    }

    return data;
  }

  function orderStatusLabel(status) {
    const labels = {
      placed: "ORDER RECEIVED",
      pending: "ORDER RECEIVED",
      confirmed: "CONFIRMED",
      packing: "PACKING",
      packed: "READY",
      out_for_delivery: "OUT FOR DELIVERY",
      delivered: "DELIVERED",
      cancelled: "CANCELLED",
      refunded: "REFUNDED"
    };

    return labels[status] ||
      String(status || "").replaceAll("_", " ").toUpperCase();
  }

  function openMyOrders() {
    let old = document.getElementById("delyvoMyOrders");
    if (old) old.remove();

    const modal = document.createElement("div");
    modal.id = "delyvoMyOrders";

    modal.innerHTML = `
      <div class="mo-backdrop"></div>

      <div class="mo-card">
        <div class="mo-head">
          <div>
            <h2>My Orders</h2>
            <p>Your Delyvo grocery orders</p>
          </div>

          <button class="mo-close" id="moClose">×</button>
        </div>

        <div id="moOrdersList">
          <p class="mo-loading">Loading orders...</p>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("moClose").onclick =
      () => modal.remove();

    loadMyOrders();
  }

  async function loadMyOrders() {
    const box = document.getElementById("moOrdersList");

    if (!box) return;

    try {
      const orders = await customerApi(
        "/rest/v1/orders" +
        "?select=id,order_number,status,payment_status,subtotal,delivery_fee,total,created_at" +
        "&order=created_at.desc"
      );

      if (!orders.length) {
        box.innerHTML = `
          <div class="mo-empty">
            <div>🛍️</div>
            <strong>No orders yet</strong>
            <p>Your orders will appear here.</p>
          </div>
        `;
        return;
      }

      box.innerHTML = "";

      orders.forEach(order => {
        const card = document.createElement("div");
        card.className = "mo-order";

        card.innerHTML = `
          <div class="mo-order-top">
            <div>
              <strong>${escapeHtml(order.order_number)}</strong>
              <small>${formatDate(order.created_at)}</small>
            </div>

            <span class="mo-status mo-${escapeHtml(order.status)}">
              ${orderStatusLabel(order.status)}
            </span>
          </div>

          <div class="mo-details">
            <div>
              <span>Subtotal</span>
              <strong>₹${Number(order.subtotal || 0).toFixed(0)}</strong>
            </div>

            <div>
              <span>Delivery</span>
              <strong>₹${Number(order.delivery_fee || 0).toFixed(0)}</strong>
            </div>

            <div>
              <span>Total</span>
              <strong>₹${Number(order.total || 0).toFixed(0)}</strong>
            </div>
          </div>

          <div class="mo-payment">
            <span>Payment: ${escapeHtml(
              order.payment_status || "pending"
            ).toUpperCase()}</span>

            <span>Cash on Delivery</span>
          </div>
        `;

        box.appendChild(card);
      });

    } catch (e) {
      box.innerHTML = `
        <div class="mo-error">
          ${escapeHtml(e.message)}
        </div>
      `;
    }
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

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.openMyOrders = openMyOrders;

  const style = document.createElement("style");

  style.textContent = `
    #delyvoMyOrders {
      position:fixed;
      inset:0;
      z-index:99998;
    }

    .mo-backdrop {
      position:absolute;
      inset:0;
      background:rgba(0,0,0,.55);
    }

    .mo-card {
      position:relative;
      z-index:2;
      width:min(94%,700px);
      max-height:86vh;
      overflow:auto;
      box-sizing:border-box;
      margin:7vh auto 0;
      padding:22px;
      background:#fff;
      border-radius:20px;
      box-shadow:0 15px 50px rgba(0,0,0,.25);
    }

    .mo-head {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:15px;
      margin-bottom:18px;
    }

    .mo-head h2 {
      margin:0;
    }

    .mo-head p {
      margin:4px 0 0;
      color:#777;
    }

    .mo-close {
      width:38px;
      height:38px;
      border:0;
      border-radius:50%;
      background:#f2f2f2;
      font-size:25px;
      cursor:pointer;
    }

    .mo-order {
      padding:16px;
      margin-bottom:12px;
      border:1px solid #eee;
      border-radius:14px;
      background:#fafafa;
    }

    .mo-order-top {
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:12px;
    }

    .mo-order-top strong,
    .mo-order-top small {
      display:block;
    }

    .mo-order-top small {
      color:#777;
      margin-top:4px;
    }

    .mo-status {
      padding:6px 9px;
      border-radius:20px;
      font-size:10px;
      font-weight:800;
      background:#eee;
    }

    .mo-placed,
    .mo-pending {
      background:#fff1c7;
      color:#8a5b00;
    }

    .mo-confirmed,
    .mo-packing,
    .mo-packed {
      background:#e7f0ff;
      color:#2457a6;
    }

    .mo-out_for_delivery,
    .mo-delivered {
      background:#d9f7df;
      color:#08752b;
    }

    .mo-cancelled,
    .mo-refunded {
      background:#ffe2e2;
      color:#a40000;
    }

    .mo-details {
      display:grid;
      grid-template-columns:repeat(3,1fr);
      gap:10px;
      margin-top:15px;
    }

    .mo-details div {
      padding:10px;
      border-radius:10px;
      background:#fff;
    }

    .mo-details span {
      display:block;
      color:#777;
      font-size:12px;
      margin-bottom:4px;
    }

    .mo-payment {
      display:flex;
      justify-content:space-between;
      gap:10px;
      margin-top:12px;
      padding-top:12px;
      border-top:1px solid #eee;
      color:#666;
      font-size:13px;
    }

    .mo-loading,
    .mo-empty,
    .mo-error {
      padding:30px;
      text-align:center;
    }

    .mo-empty div {
      font-size:35px;
      margin-bottom:10px;
    }

    .mo-empty p {
      color:#777;
    }

    .mo-error {
      color:#b00020;
    }

    @media(max-width:600px) {
      .mo-card {
        width:96%;
        margin-top:3vh;
        padding:16px;
      }

      .mo-order-top {
        align-items:flex-start;
        flex-direction:column;
      }

      .mo-details {
        grid-template-columns:1fr;
      }

      .mo-payment {
        align-items:flex-start;
        flex-direction:column;
      }
    }
  `;

  document.head.appendChild(style);
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("CUSTOMER MY ORDERS ADDED")
