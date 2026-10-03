from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  function shopToken() {
    return localStorage.getItem("delyvo_shop_token") || "";
  }

  async function orderApi(path, options = {}) {
    const r = await fetch(URL + path, {
      ...options,
      headers: {
        apikey: KEY,
        Authorization: "Bearer " + shopToken(),
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });

    const data = await r.json().catch(() => null);

    if (!r.ok) {
      throw new Error(
        data?.message ||
        data?.msg ||
        data?.error ||
        "Order request failed"
      );
    }

    return data;
  }

  function nextStatus(status) {
    const flow = {
      placed: "confirmed",
      pending: "confirmed",
      confirmed: "packing",
      packing: "packed",
      packed: "out_for_delivery",
      out_for_delivery: "delivered"
    };

    return flow[status] || null;
  }

  function statusLabel(status) {
    const labels = {
      placed: "NEW",
      pending: "NEW",
      confirmed: "CONFIRMED",
      packing: "PACKING",
      packed: "READY",
      out_for_delivery: "OUT FOR DELIVERY",
      delivered: "DELIVERED",
      cancelled: "CANCELLED"
    };

    return labels[status] || String(status || "").toUpperCase();
  }

  async function changeOrderStatus(orderId, status, button) {
    button.disabled = true;
    button.textContent = "Saving...";

    try {
      await orderApi(
        "/rest/v1/rpc/transition_order_status",
        {
          method: "POST",
          body: JSON.stringify({
            p_order_id: orderId,
            p_new_status: status
          })
        }
      );

      button.textContent = "Saved ✓";

      setTimeout(() => {
        loadShopOrders();
      }, 500);

    } catch (e) {
      alert(e.message);
      button.disabled = false;
      button.textContent = "Update";
    }
  }

  async function loadShopOrders() {
    const box = document.getElementById("delyvoShopOrders");
    if (!box || !shopToken()) return;

    box.innerHTML = "<p>Orders loading...</p>";

    try {
      const orders = await orderApi(
        "/rest/v1/orders" +
        "?select=id,order_number,status,payment_status,subtotal,delivery_fee,total,created_at,address_id" +
        "&order=created_at.desc"
      );

      if (!orders.length) {
        box.innerHTML = `
          <div class="so-empty">
            <strong>No orders yet</strong>
            <p>Customer order aayega to yahan dikhega.</p>
          </div>
        `;
        return;
      }

      box.innerHTML = "";

      orders.forEach(order => {
        const card = document.createElement("div");
        card.className = "so-card";

        const next = nextStatus(order.status);

        card.innerHTML = `
          <div class="so-top">
            <div>
              <strong>${escapeHtml(order.order_number)}</strong>
              <small>${formatDate(order.created_at)}</small>
            </div>

            <span class="so-status so-${escapeHtml(order.status)}">
              ${statusLabel(order.status)}
            </span>
          </div>

          <div class="so-money">
            <span>Subtotal ₹${Number(order.subtotal || 0).toFixed(0)}</span>
            <span>Delivery ₹${Number(order.delivery_fee || 0).toFixed(0)}</span>
            <strong>Total ₹${Number(order.total || 0).toFixed(0)}</strong>
          </div>

          <div class="so-bottom">
            <span>Payment: ${escapeHtml(order.payment_status || "pending").toUpperCase()}</span>

            ${
              next
                ? `<button class="so-update">
                    ${next === "confirmed" ? "Accept Order" :
                      next === "packing" ? "Start Packing" :
                      next === "packed" ? "Mark Ready" :
                      next === "out_for_delivery" ? "Send for Delivery" :
                      "Mark Delivered"}
                  </button>`
                : `<span class="so-done">${statusLabel(order.status)}</span>`
            }
          </div>
        `;

        const btn = card.querySelector(".so-update");

        if (btn) {
          btn.onclick = () =>
            changeOrderStatus(order.id, next, btn);
        }

        box.appendChild(card);
      });

    } catch (e) {
      box.innerHTML =
        "<p style='color:#b00020'>Orders load nahi hue: " +
        escapeHtml(e.message) +
        "</p>";
    }
  }

  function formatDate(value) {
    try {
      return new Date(value).toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
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

  function addOrdersSection() {
    if (document.getElementById("delyvoShopOrdersPanel")) return;

    const panel = document.createElement("section");
    panel.id = "delyvoShopOrdersPanel";

    panel.innerHTML = `
      <div class="so-head">
        <div>
          <h2>Orders</h2>
          <p>Customer orders yahan manage karo.</p>
        </div>

        <button id="soRefresh">Refresh Orders</button>
      </div>

      <div id="delyvoShopOrders"></div>
    `;

    document.body.appendChild(panel);

    document.getElementById("soRefresh").onclick =
      loadShopOrders;
  }

  function addOrderStyle() {
    const style = document.createElement("style");

    style.textContent = `
      #delyvoShopOrdersPanel {
        max-width:1100px;
        margin:24px auto;
        padding:20px;
        background:#fff;
        border-radius:16px;
        box-shadow:0 4px 20px rgba(0,0,0,.08);
      }

      .so-head {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:15px;
        margin-bottom:18px;
      }

      .so-head h2 {
        margin:0 0 5px;
      }

      .so-head p {
        margin:0;
        color:#666;
      }

      #soRefresh {
        border:0;
        padding:10px 15px;
        border-radius:9px;
        background:#111;
        color:#fff;
        cursor:pointer;
      }

      .so-card {
        border:1px solid #eee;
        border-radius:14px;
        padding:16px;
        margin-bottom:12px;
        background:#fafafa;
      }

      .so-top {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:15px;
      }

      .so-top strong,
      .so-top small {
        display:block;
      }

      .so-top small {
        color:#777;
        margin-top:4px;
      }

      .so-status {
        padding:6px 9px;
        border-radius:20px;
        font-size:11px;
        font-weight:700;
        background:#eee;
      }

      .so-placed,
      .so-pending {
        background:#fff1c7;
        color:#8a5b00;
      }

      .so-confirmed,
      .so-packing,
      .so-packed {
        background:#e7f0ff;
        color:#2457a6;
      }

      .so-out_for_delivery {
        background:#e4f7e8;
        color:#16752b;
      }

      .so-delivered {
        background:#d9f7df;
        color:#08752b;
      }

      .so-cancelled {
        background:#ffe2e2;
        color:#a40000;
      }

      .so-money {
        display:flex;
        flex-wrap:wrap;
        gap:18px;
        margin:16px 0;
        color:#666;
      }

      .so-money strong {
        color:#111;
      }

      .so-bottom {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:12px;
        border-top:1px solid #eee;
        padding-top:12px;
      }

      .so-update {
        border:0;
        padding:10px 15px;
        border-radius:9px;
        background:#111;
        color:#fff;
        cursor:pointer;
      }

      .so-update:disabled {
        opacity:.6;
      }

      .so-done {
        color:#777;
        font-weight:700;
      }

      .so-empty {
        padding:30px;
        text-align:center;
        color:#777;
      }

      @media(max-width:600px) {
        .so-head,
        .so-top,
        .so-bottom {
          align-items:flex-start;
          flex-direction:column;
        }

        #soRefresh,
        .so-update {
          width:100%;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function startOrderWorkflow() {
    addOrderStyle();
    addOrdersSection();
    loadShopOrders();
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      startOrderWorkflow
    );
  } else {
    startOrderWorkflow();
  }
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("SHOP ORDER WORKFLOW ADDED")
