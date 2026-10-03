from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  function showDelyvoOrderSuccess(order) {
    let old = document.getElementById("delyvoOrderSuccess");
    if (old) old.remove();

    const modal = document.createElement("div");
    modal.id = "delyvoOrderSuccess";

    modal.innerHTML = `
      <div class="dos-backdrop"></div>

      <div class="dos-card">
        <div class="dos-check">✓</div>

        <h2>Order Placed Successfully</h2>

        <p class="dos-thanks">
          Thank you for shopping with Delyvo.
        </p>

        <div class="dos-order">
          <span>Order Number</span>
          <strong>${escapeHtml(order.order_number || "")}</strong>
        </div>

        <div class="dos-row">
          <span>Subtotal</span>
          <strong>₹${Number(order.subtotal || 0).toFixed(0)}</strong>
        </div>

        <div class="dos-row">
          <span>Delivery Fee</span>
          <strong>₹${Number(order.delivery_fee || 0).toFixed(0)}</strong>
        </div>

        <div class="dos-total">
          <span>Total</span>
          <strong>₹${Number(order.total || 0).toFixed(0)}</strong>
        </div>

        <div class="dos-cod">
          💵 Cash on Delivery
        </div>

        <button class="dos-primary" id="dosContinue">
          Continue Shopping
        </button>

        <button class="dos-secondary" id="dosOrders">
          My Orders
        </button>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("dosContinue").onclick = () => {
      modal.remove();
      window.scrollTo({top: 0, behavior: "smooth"});
    };

    document.getElementById("dosOrders").onclick = () => {
      modal.remove();

      if (typeof window.openMyOrders === "function") {
        window.openMyOrders();
      } else {
        alert("My Orders section next update mein available hoga.");
      }
    };
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.showDelyvoOrderSuccess = showDelyvoOrderSuccess;

  const style = document.createElement("style");

  style.textContent = `
    #delyvoOrderSuccess {
      position:fixed;
      inset:0;
      z-index:99999;
    }

    .dos-backdrop {
      position:absolute;
      inset:0;
      background:rgba(0,0,0,.55);
    }

    .dos-card {
      position:relative;
      z-index:2;
      width:min(92%,430px);
      box-sizing:border-box;
      margin:8vh auto 0;
      padding:28px;
      background:#fff;
      border-radius:22px;
      box-shadow:0 15px 50px rgba(0,0,0,.25);
      text-align:center;
    }

    .dos-check {
      width:68px;
      height:68px;
      margin:0 auto 15px;
      border-radius:50%;
      display:flex;
      align-items:center;
      justify-content:center;
      background:#dff7e4;
      color:#11852e;
      font-size:38px;
      font-weight:800;
    }

    .dos-card h2 {
      margin:0;
      font-size:24px;
    }

    .dos-thanks {
      color:#777;
      margin:8px 0 22px;
    }

    .dos-order {
      padding:14px;
      border-radius:12px;
      background:#f7f7f7;
      margin-bottom:15px;
    }

    .dos-order span {
      display:block;
      color:#777;
      font-size:13px;
      margin-bottom:5px;
    }

    .dos-order strong {
      font-size:19px;
    }

    .dos-row,
    .dos-total {
      display:flex;
      justify-content:space-between;
      gap:15px;
      padding:8px 0;
    }

    .dos-row {
      color:#666;
    }

    .dos-total {
      margin-top:8px;
      padding-top:14px;
      border-top:1px solid #eee;
      font-size:18px;
    }

    .dos-cod {
      margin:18px 0;
      padding:12px;
      border-radius:10px;
      background:#fff7df;
      color:#7b5a00;
      font-weight:700;
    }

    .dos-primary,
    .dos-secondary {
      width:100%;
      padding:12px;
      border-radius:10px;
      cursor:pointer;
      font-size:15px;
    }

    .dos-primary {
      border:0;
      background:#111;
      color:#fff;
    }

    .dos-secondary {
      margin-top:9px;
      border:1px solid #ddd;
      background:#fff;
      color:#222;
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
print("CUSTOMER ORDER SUCCESS SCREEN ADDED")
