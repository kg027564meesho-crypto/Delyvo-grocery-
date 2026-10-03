from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  function showFinalOrderSuccess(order) {
    const old = document.getElementById("delyvoFinalSuccess");
    if (old) old.remove();

    const modal = document.createElement("div");
    modal.id = "delyvoFinalSuccess";

    modal.innerHTML = `
      <div class="fos-backdrop"></div>

      <div class="fos-card">
        <div class="fos-icon">✓</div>

        <h2>Order Placed!</h2>

        <p class="fos-thanks">
          Thank you for ordering from Delyvo.
        </p>

        <div class="fos-order">
          <span>Order Number</span>
          <strong>
            ${escapeHtml(order?.order_number || "Delyvo Order")}
          </strong>
        </div>

        <div class="fos-order">
          <span>Total Amount</span>
          <strong>
            ₹${Number(order?.total || 0).toFixed(0)}
          </strong>
        </div>

        <div class="fos-status">
          <span>●</span>
          Order received
        </div>

        <button id="fosOrders">
          View My Orders
        </button>

        <button id="fosContinue">
          Continue Shopping
        </button>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("fosOrders").onclick = () => {
      modal.remove();

      if (typeof window.openMyOrders === "function") {
        window.openMyOrders();
      }
    };

    document.getElementById("fosContinue").onclick = () => {
      modal.remove();
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

  window.showDelyvoOrderSuccess =
    showFinalOrderSuccess;

  const style =
    document.createElement("style");

  style.textContent = `
    #delyvoFinalSuccess {
      position:fixed;
      inset:0;
      z-index:99999;
    }

    .fos-backdrop {
      position:absolute;
      inset:0;
      background:rgba(0,0,0,.55);
    }

    .fos-card {
      position:relative;
      z-index:2;
      width:min(92%,430px);
      margin:10vh auto 0;
      padding:28px;
      text-align:center;
      background:#fff;
      border-radius:20px;
      box-shadow:0 18px 60px rgba(0,0,0,.25);
    }

    .fos-icon {
      width:62px;
      height:62px;
      margin:0 auto 14px;
      display:flex;
      align-items:center;
      justify-content:center;
      border-radius:50%;
      background:#d9f7df;
      color:#08752b;
      font-size:34px;
      font-weight:800;
    }

    .fos-card h2 {
      margin:0;
    }

    .fos-thanks {
      color:#777;
    }

    .fos-order {
      display:flex;
      justify-content:space-between;
      gap:12px;
      padding:12px;
      margin-top:8px;
      border-radius:10px;
      background:#f7f7f7;
      text-align:left;
    }

    .fos-order span {
      color:#777;
    }

    .fos-status {
      margin:16px 0;
      padding:10px;
      border-radius:9px;
      background:#eef7ee;
      color:#28752d;
      font-weight:700;
    }

    .fos-status span {
      margin-right:5px;
    }

    #fosOrders,
    #fosContinue {
      width:100%;
      padding:12px;
      border-radius:10px;
      cursor:pointer;
      font-weight:700;
    }

    #fosOrders {
      border:0;
      background:#111;
      color:#fff;
    }

    #fosContinue {
      margin-top:8px;
      border:1px solid #ddd;
      background:#fff;
    }
  `;

  document.head.appendChild(style);
})();
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

print("CUSTOMER FINAL ORDER FLOW ADDED")
