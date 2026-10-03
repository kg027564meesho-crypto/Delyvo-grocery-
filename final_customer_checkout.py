from pathlib import Path

p = Path("grocery/app.js")
html = p.read_text()

script = r'''
<script>
/* =========================================================
   DELYVO - FINAL CUSTOMER CHECKOUT + COD ORDER FLOW
   ========================================================= */

window.finalDelyvoCheckout = async function () {
  try {
    const token = getAccessToken();

    if (!token) {
      openLogin();
      return;
    }

    const user = await getAuthUser();

    if (!user || !user.id) {
      throw new Error("Customer session nahi mili. Dobara login karein.");
    }

    let address = null;

    try {
      address = JSON.parse(
        localStorage.getItem("delyvo_grocery_address") || "null"
      );
    } catch (_) {
      address = null;
    }

    if (!address || !address.id) {
      throw new Error("Pehle delivery address select karein.");
    }

    if (String(address.pincode).trim() !== "201204") {
      throw new Error(
        "Abhi Delyvo delivery sirf Modinagar 201204 mein available hai."
      );
    }

    if (!Array.isArray(cart) || cart.length === 0) {
      throw new Error("Cart khali hai.");
    }

    const items = cart.map(item => ({
      id: item.id || item.variant_id || item.product_id,
      quantity: Number(item.quantity || 1)
    })).filter(item => item.id && item.quantity > 0);

    if (!items.length) {
      throw new Error("Cart mein valid products nahi mile.");
    }

    let checkoutSubtotal = 0;

    cart.forEach(item => {
      const price = Number(
        item.price ??
        item.selling_price ??
        item.unit_price ??
        item.sale_price ??
        0
      );

      checkoutSubtotal += price * Number(item.quantity || 1);
    });

    if (checkoutSubtotal < 199) {
      throw new Error(
        "Minimum order value ₹199 hai. Cart mein aur items add karein."
      );
    }

    const checkoutDelivery = 29;
    const checkoutTotal = checkoutSubtotal + checkoutDelivery;

    const response = await fetch(
      `${SUPABASE_URL}/rest/v1/rpc/create_grocery_order`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          p_address_id: address.id,
          p_items: items,
          p_notes: null
        })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.message ||
        data.hint ||
        data.details ||
        data.error ||
        "Order place nahi ho paya."
      );
    }

    const result = Array.isArray(data) ? data[0] : data;

    if (!result) {
      throw new Error("Order response nahi mila.");
    }

    /* Clear cart only after successful order */
    cart = [];
    saveCart();

    /* Close checkout if present */
    [
      "checkoutModal",
      "cartModal",
      "cartDrawer"
    ].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.remove("open", "show");
    });

    /* Refresh cart UI */
    if (typeof renderCart === "function") {
      renderCart();
    }

    /* Final success screen */
    if (typeof showDelyvoOrderSuccess === "function") {
      showDelyvoOrderSuccess({
        ...result,
        order_number: result.order_number || "Order placed",
        subtotal:
          result.subtotal != null
            ? result.subtotal
            : checkoutSubtotal,
        delivery_fee:
          result.delivery_fee != null
            ? result.delivery_fee
            : checkoutDelivery,
        total:
          result.total != null
            ? result.total
            : checkoutTotal,
        payment_method: "COD",
        payment_status: result.payment_status || "pending"
      });
    } else {
      alert(
        "Order placed successfully!\n\n" +
        "Order Number: " +
        (result.order_number || "DLV")
      );
    }

    return result;

  } catch (error) {
    console.error("DELYVO CHECKOUT ERROR:", error);

    const message = error?.message || "Order place nahi ho paya.";

    if (typeof showToast === "function") {
      showToast(message);
    } else {
      alert(message);
    }

    throw error;
  }
};


/* Final placeOrder function used by checkout button */
window.placeOrder = async function () {
  return await window.finalDelyvoCheckout();
};


/* Final checkout opener */
window.openCheckout = function () {
  const token = getAccessToken();

  if (!token) {
    openLogin();
    return;
  }

  let address = null;

  try {
    address = JSON.parse(
      localStorage.getItem("delyvo_grocery_address") || "null"
    );
  } catch (_) {
    address = null;
  }

  if (!address || !address.id) {
    alert("Pehle delivery address select karein.");
    if (typeof openAddressManager === "function") {
      openAddressManager();
    } else if (typeof openLocationModal === "function") {
      openLocationModal();
    }
    return;
  }

  if (!Array.isArray(cart) || cart.length === 0) {
    alert("Cart khali hai.");
    return;
  }

  let subtotal = 0;

  cart.forEach(item => {
    const price = Number(
      item.price ??
      item.selling_price ??
      item.unit_price ??
      item.sale_price ??
      0
    );

    subtotal += price * Number(item.quantity || 1);
  });

  const delivery = subtotal >= 199 ? 29 : 0;
  const total = subtotal + delivery;

  let modal = document.getElementById("checkoutModal");

  if (!modal) {
    modal = document.createElement("div");
    modal.id = "checkoutModal";
    modal.className = "modal";

    modal.innerHTML = `
      <div class="modal-card checkout-card">
        <div class="drawer-head">
          <h2>Checkout</h2>
          <button class="close-btn"
                  onclick="closePanel('checkoutModal')">×</button>
        </div>

        <div id="checkoutSummary"></div>

        <div class="checkout-address-box">
          <strong>Delivery Address</strong>
          <p id="checkoutAddressText"></p>
        </div>

        <div class="checkout-payment-box">
          <strong>Payment Method</strong>
          <label>
            <input type="radio"
                   name="delyvoPaymentMethod"
                   value="cod"
                   checked>
            Cash on Delivery
          </label>
        </div>

        <button class="primary-btn"
                id="finalPlaceOrderBtn"
                type="button">
          Place Order • COD
        </button>
      </div>
    `;

    document.body.appendChild(modal);

    document
      .getElementById("finalPlaceOrderBtn")
      .addEventListener("click", async function () {
        this.disabled = true;
        this.textContent = "Placing Order...";

        try {
          await window.finalDelyvoCheckout();
        } catch (_) {
          this.disabled = false;
          this.textContent = "Place Order • COD";
        }
      });
  }

  const summary = document.getElementById("checkoutSummary");

  if (summary) {
    summary.innerHTML = `
      <div class="checkout-row">
        <span>Subtotal</span>
        <strong>₹${subtotal.toFixed(2)}</strong>
      </div>

      <div class="checkout-row">
        <span>Delivery</span>
        <strong>₹${delivery.toFixed(2)}</strong>
      </div>

      <div class="checkout-row checkout-total">
        <span>Total</span>
        <strong>₹${total.toFixed(2)}</strong>
      </div>
    `;
  }

  const addressText =
    document.getElementById("checkoutAddressText");

  if (addressText) {
    addressText.textContent =
      [
        address.recipient_name,
        address.phone,
        address.address_line1,
        address.address_line2,
        address.landmark,
        address.city,
        address.state,
        address.pincode
      ]
      .filter(Boolean)
      .join(", ");
  }

  modal.classList.add("open", "show");
};


/* Checkout styling */
if (!document.getElementById("delyvo-final-checkout-css")) {
  const style = document.createElement("style");
  style.id = "delyvo-final-checkout-css";

  style.textContent = `
    .checkout-card {
      max-width: 520px;
    }

    .checkout-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid #eee;
    }

    .checkout-total {
      font-size: 20px;
      border-bottom: 0;
      padding-top: 16px;
    }

    .checkout-address-box,
    .checkout-payment-box {
      margin-top: 16px;
      padding: 14px;
      border: 1px solid #eee;
      border-radius: 12px;
    }

    .checkout-address-box p {
      margin: 8px 0 0;
      line-height: 1.5;
    }

    .checkout-payment-box label {
      display: block;
      margin-top: 10px;
    }

    #finalPlaceOrderBtn {
      width: 100%;
      margin-top: 18px;
    }
  `;

  document.head.appendChild(style);
}

</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)

print("FINAL CUSTOMER CHECKOUT + COD FLOW ADDED")
