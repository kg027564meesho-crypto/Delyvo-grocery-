from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  function getCartData() {
    try {
      return JSON.parse(
        localStorage.getItem("delyvo_grocery_cart") || "[]"
      );
    } catch {
      return [];
    }
  }

  function saveCartData(cart) {
    localStorage.setItem(
      "delyvo_grocery_cart",
      JSON.stringify(cart)
    );
  }

  function renderFinalCart() {
    const cart = getCartData();

    const count = cart.reduce(
      (sum, item) => sum + Number(item.quantity || 0),
      0
    );

    const subtotal = cart.reduce(
      (sum, item) =>
        sum +
        Number(item.price || 0) *
        Number(item.quantity || 0),
      0
    );

    const delivery = subtotal >= 199 ? 29 : 0;
    const total = subtotal + delivery;

    const countEl =
      document.getElementById("cartCount");

    if (countEl) {
      countEl.textContent = count;
    }

    const box =
      document.getElementById("cartItems") ||
      document.getElementById("cartContent");

    if (!box) return;

    if (!cart.length) {
      box.innerHTML = `
        <div class="dc-empty-cart">
          <div class="dc-empty-icon">🛒</div>
          <h3>Your cart is empty</h3>
          <p>Add grocery products to continue.</p>
        </div>
      `;
      updateCartTotals(0, 0, 0);
      return;
    }

    box.innerHTML = cart.map((item, index) => {
      const qty = Number(item.quantity || 0);
      const price = Number(item.price || 0);
      const line = price * qty;

      return `
        <div class="dc-cart-item">
          <div class="dc-cart-info">
            <strong>${escapeHtml(item.name)}</strong>
            <small>₹${price}</small>
          </div>

          <div class="dc-cart-actions">
            <button
              class="dc-qty"
              data-action="minus"
              data-index="${index}"
            >−</button>

            <span>${qty}</span>

            <button
              class="dc-qty"
              data-action="plus"
              data-index="${index}"
            >+</button>

            <strong>₹${line}</strong>

            <button
              class="dc-remove"
              data-action="remove"
              data-index="${index}"
            >Remove</button>
          </div>
        </div>
      `;
    }).join("");

    box.querySelectorAll("[data-action]").forEach(button => {
      button.onclick = () => {
        const index =
          Number(button.dataset.index);

        const action =
          button.dataset.action;

        const current = getCartData();

        if (!current[index]) return;

        if (action === "plus") {
          current[index].quantity =
            Number(current[index].quantity || 0) + 1;
        }

        if (action === "minus") {
          current[index].quantity =
            Number(current[index].quantity || 0) - 1;

          if (current[index].quantity <= 0) {
            current.splice(index, 1);
          }
        }

        if (action === "remove") {
          current.splice(index, 1);
        }

        saveCartData(current);
        renderFinalCart();
      });
    });

    updateCartTotals(
      subtotal,
      delivery,
      total
    );
  }

  function updateCartTotals(
    subtotal,
    delivery,
    total
  ) {
    const subtotalEl =
      document.getElementById("cartSubtotal");

    const deliveryEl =
      document.getElementById("cartDelivery");

    const totalEl =
      document.getElementById("cartTotal");

    if (subtotalEl) {
      subtotalEl.textContent =
        "₹" + subtotal.toFixed(0);
    }

    if (deliveryEl) {
      deliveryEl.textContent =
        "₹" + delivery.toFixed(0);
    }

    if (totalEl) {
      totalEl.textContent =
        "₹" + total.toFixed(0);
    }

    const minMessage =
      document.getElementById("cartMinimumMessage");

    if (minMessage) {
      if (subtotal > 0 && subtotal < 199) {
        minMessage.textContent =
          "Minimum order ₹199 hai.";
        minMessage.style.display = "block";
      } else {
        minMessage.style.display = "none";
      }
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

  window.renderFinalCart = renderFinalCart;

  const style =
    document.createElement("style");

  style.textContent = `
    .dc-empty-cart {
      text-align:center;
      padding:40px 20px;
      color:#777;
    }

    .dc-empty-icon {
      font-size:45px;
      margin-bottom:10px;
    }

    .dc-cart-item {
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:15px;
      padding:14px 0;
      border-bottom:1px solid #eee;
    }

    .dc-cart-info strong,
    .dc-cart-info small {
      display:block;
    }

    .dc-cart-info small {
      color:#777;
      margin-top:5px;
    }

    .dc-cart-actions {
      display:flex;
      align-items:center;
      gap:8px;
      flex-wrap:wrap;
    }

    .dc-qty {
      width:32px;
      height:32px;
      border:1px solid #ddd;
      border-radius:8px;
      background:#fff;
      cursor:pointer;
      font-size:18px;
    }

    .dc-remove {
      border:0;
      background:transparent;
      color:#b00020;
      cursor:pointer;
      font-size:12px;
    }

    #cartMinimumMessage {
      padding:10px;
      margin-top:10px;
      border-radius:8px;
      background:#fff3cd;
      color:#8a5b00;
      font-weight:700;
    }

    @media(max-width:600px) {
      .dc-cart-item {
        align-items:flex-start;
        flex-direction:column;
      }

      .dc-cart-actions {
        width:100%;
      }
    }
  `;

  document.head.appendChild(style);

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      renderFinalCart
    );
  } else {
    renderFinalCart();
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

print("CUSTOMER CART COMPLETION ADDED")
