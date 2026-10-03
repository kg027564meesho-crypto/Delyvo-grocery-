from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  function addCODCheckout() {
    if (document.getElementById("delyvoCODBox")) return;

    const checkout =
      document.getElementById("checkoutModal");

    if (!checkout) return;

    const box = document.createElement("div");
    box.id = "delyvoCODBox";

    box.innerHTML = `
      <div class="cod-title">Payment Method</div>

      <label class="cod-option">
        <input
          type="radio"
          name="delyvoPaymentMethod"
          value="cod"
          checked
        >
        <span>
          <strong>Cash on Delivery</strong>
          <small>Delivery ke time cash pay karein.</small>
        </span>
      </label>

      <div class="cod-note">
        Abhi Delyvo par Cash on Delivery available hai.
      </div>
    `;

    const summary =
      document.getElementById("checkoutSummary");

    if (summary) {
      summary.appendChild(box);
    } else {
      checkout.appendChild(box);
    }
  }

  const style =
    document.createElement("style");

  style.textContent = `
    #delyvoCODBox {
      margin-top:16px;
      padding:14px;
      border:1px solid #ddd;
      border-radius:12px;
      background:#fafafa;
    }

    .cod-title {
      font-weight:700;
      margin-bottom:10px;
    }

    .cod-option {
      display:flex;
      gap:10px;
      align-items:flex-start;
      cursor:pointer;
    }

    .cod-option input {
      margin-top:4px;
    }

    .cod-option strong,
    .cod-option small {
      display:block;
    }

    .cod-option small {
      margin-top:4px;
      color:#777;
    }

    .cod-note {
      margin-top:10px;
      padding:9px;
      border-radius:8px;
      background:#eef7ee;
      color:#28752d;
      font-size:13px;
    }
  `;

  document.head.appendChild(style);

  window.addDelyvoCODCheckout =
    addCODCheckout;

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      addCODCheckout
    );
  } else {
    addCODCheckout();
  }
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

print("COD CHECKOUT FINALIZED")
