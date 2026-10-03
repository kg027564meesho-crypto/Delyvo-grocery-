const SUPABASE_URL = "https://unwdkreujyejgcucgttj.supabase.co";
const SUPABASE_KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

const cart = JSON.parse(localStorage.getItem("delyvo_grocery_cart") || "[]");
let selectedAddress = JSON.parse(localStorage.getItem("delyvo_grocery_address") || "null");

const categoryIcons = [
  "🥦", "🥛", "🍎", "🍞", "🍚",
  "🥤", "🧴", "🍪", "🧹", "📦"
];

async function supabaseGet(table) {
  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/${table}?select=*`,
    {
      headers: {
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${SUPABASE_KEY}`
      }
    }
  );

  if (!response.ok) {
    throw new Error(`${table}: HTTP ${response.status}`);
  }

  return response.json();
}

function renderCategories(categories) {
  const box = document.getElementById("categories");

  if (!categories.length) {
    box.innerHTML = "<p>No categories available.</p>";
    return;
  }

  box.innerHTML = categories.map((category, index) => `
    <div class="category">
      <div class="icon">${categoryIcons[index] || "🛒"}</div>
      <h3>${category.name}</h3>
    </div>
  `).join("");
}

function renderProducts(products) {
  const box = document.getElementById("products");

  if (!products.length) {
    box.innerHTML = "<p>No products available.</p>";
    return;
  }

  box.innerHTML = products.map(product => `
    <div class="product">
      <div class="product-image">
        ${product.image_url
          ? `<img src="${product.image_url}" alt="${product.name}">`
          : "🛒"}
      </div>
      <h3>${product.name}</h3>
      <div class="unit">${product.unit ?? ""}</div>
      <div class="price">
        ₹${product.selling_price ?? "--"}
        ${product.mrp && product.mrp > product.selling_price
          ? `<span class="mrp">₹${product.mrp}</span>`
          : ""}
      </div>
      <button class="add-btn" onclick="addToCart('${product.id}')">
        Add
      </button>
    </div>
  `).join("");
}

function addToCart(productId) {
  const product = window.allProducts.find(p => p.id === productId);
  if (!product) return;

  const existing = cart.find(item => item.id === productId);

  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({
      id: product.id,
      variant_id: product.id,
      product_id: product.product_id || product.id,
      name: product.name,
      variant_name: product.variant_name || product.unit || "",
      unit: product.unit,
      price: Number(
        product.selling_price ??
        product.price ??
        0
      ),
      selling_price: Number(
        product.selling_price ??
        product.price ??
        0
      ),
      mrp: Number(product.mrp || 0),
      image_url: product.image_url || null,
      quantity: 1
    });
  }

  saveCart();
}

function saveCart() {
  localStorage.setItem("delyvo_grocery_cart", JSON.stringify(cart));

  document.getElementById("cartCount").textContent =
    cart.reduce((total, item) => total + item.quantity, 0);

  renderCart();
}

function renderCart() {
  const box = document.getElementById("cartItems");

  if (!box) return;

  if (!cart.length) {
    box.innerHTML = "<p>Your cart is empty.</p>";
    document.getElementById("cartSubtotal").textContent = "₹0";
    document.getElementById("cartTotal").textContent = "₹0";
    return;
  }

  box.innerHTML = cart.map(item => `
    <div class="cart-row">
      <div class="cart-row-info">
        <strong>${item.name}</strong>
        <small>${item.unit || ""}</small>

        <div class="qty">
          <button onclick="changeQty('${item.id}', -1)">−</button>
          <span>${item.quantity}</span>
          <button onclick="changeQty('${item.id}', 1)">+</button>
          <b>₹${(Number(item.price ?? item.selling_price ?? item.unit_price ?? item.sale_price ?? 0) * Number(item.quantity || 1))}</b>
        </div>
      </div>
    </div>
  `).join("");

  const subtotal = cart.reduce(
    (sum, item) => sum + (Number(item.price ?? item.selling_price ?? item.unit_price ?? item.sale_price ?? 0) * Number(item.quantity || 1)),
    0
  );

  document.getElementById("cartSubtotal").textContent = `₹${subtotal}`;
  document.getElementById("cartTotal").textContent = `₹${subtotal}`;
}

function changeQty(productId, amount) {
  const item = cart.find(x => x.id === productId);

  if (!item) return;

  item.quantity += amount;

  if (item.quantity <= 0) {
    cart.splice(cart.indexOf(item), 1);
  }

  saveCart();
}

function openCart() {
  renderCart();
  document.getElementById("cartPanel").classList.add("open");
}

function closePanel(id) {
  document.getElementById(id).classList.remove("open");
}

async function loadHome() {
  try {
    if (typeof window.loadFinalCustomerCategories === "function") {
      await window.loadFinalCustomerCategories();
    }

    if (typeof window.loadFinalCustomerProducts === "function") {
      await window.loadFinalCustomerProducts();
    }

  } catch (error) {
    console.error("DELYVO HOME LOAD ERROR:", error);

    const categoriesBox = document.getElementById("categories");
    const productsBox = document.getElementById("products");

    if (categoriesBox) {
      categoriesBox.innerHTML =
        "<p>Unable to load categories.</p>";
    }

    if (productsBox) {
      productsBox.innerHTML =
        "<p>Unable to load products.</p>";
    }
  }
}


document.getElementById("searchInput").addEventListener("input", function () {
  const query = this.value.trim().toLowerCase();

  const filtered = window.allProducts.filter(product =>
    (product.name || "").toLowerCase().includes(query) ||
    (product.short_description || "").toLowerCase().includes(query) ||
    (product.sku || "").toLowerCase().includes(query)
  );

  renderProducts(filtered);
});


document.getElementById("cartBtn").onclick = openCart;

saveCart();


async function authLogin(email, password) {
  const response = await fetch(
    `${SUPABASE_URL}/auth/v1/token?grant_type=password`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SUPABASE_KEY
      },
      body: JSON.stringify({
        email,
        password
      })
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.msg || data.message || data.error_description || "Login failed");
  }

  localStorage.setItem("delyvo_access_token", data.access_token);
  localStorage.setItem("delyvo_refresh_token", data.refresh_token);

  return data;
}

async function authSignup(email, password) {
  const response = await fetch(
    `${SUPABASE_URL}/auth/v1/signup`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SUPABASE_KEY
      },
      body: JSON.stringify({
        email,
        password
      })
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.msg || data.message || data.error_description || "Signup failed");
  }

  return data;
}

window.authLogin = authLogin;
window.authSignup = authSignup;




/* ===== DELYVO GROCERY FINAL MVP ===== */

function getAccessToken() {
  return localStorage.getItem("delyvo_access_token");
}

async function getAuthUser() {
  const token = getAccessToken();
  if (!token) return null;

  const response = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${token}`
    }
  });

  if (!response.ok) {
    localStorage.removeItem("delyvo_access_token");
    localStorage.removeItem("delyvo_refresh_token");
    return null;
  }

  return response.json();
}

function openLogin() {
  document.getElementById("authModal").classList.add("open");
}

window.openLogin = openLogin;

async function updateLoginButton() {
  const btn = document.getElementById("loginBtn");
  if (!btn) return;

  const user = await getAuthUser();

  if (user) {
    btn.textContent = "Account";
    btn.onclick = async () => {
      if (confirm("Logout karna hai?")) {
        localStorage.removeItem("delyvo_access_token");
        localStorage.removeItem("delyvo_refresh_token");
        btn.textContent = "Login";
        btn.onclick = openLogin;
      }
    };
  } else {
    btn.textContent = "Login";
    btn.onclick = openLogin;
  }
}

window.updateLoginButton = updateLoginButton;

window.saveAddressToDatabase = async function(address) {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Pehle customer login karein.");
  }

  const user = await getAuthUser();

  if (!user || !user.id) {
    throw new Error("Customer session nahi mili. Dobara login karein.");
  }

  if (String(address.pincode).trim() !== "201204") {
    throw new Error("Abhi Delyvo delivery sirf Modinagar 201204 mein available hai.");
  }

  const payload = {
    user_id: user.id,
    label: address.label || "Home",
    recipient_name: address.recipient_name || "",
    phone: address.phone || "",
    address_line1: address.address_line1 || "",
    address_line2: address.address_line2 || null,
    landmark: address.landmark || null,
    city: address.city || "Modinagar",
    state: address.state || "Uttar Pradesh",
    pincode: String(address.pincode).trim(),
    latitude: address.latitude || null,
    longitude: address.longitude || null,
    is_default: !!address.is_default
  };

  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/addresses`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${token}`,
        Prefer: "return=representation"
      },
      body: JSON.stringify(payload)
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message ||
      data.hint ||
      data.details ||
      "Address save nahi ho paya."
    );
  }

  const saved = Array.isArray(data) ? data[0] : data;

  if (saved && saved.id) {
    localStorage.setItem(
      "delyvo_grocery_address",
      JSON.stringify(saved)
    );
  }

  return saved;
};

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
    if (typeof window.openAddressManager === "function") {
      window.openAddressManager();
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


/* =========================================================
   DELYVO CUSTOMER - FINAL LIVE PRODUCT DATA
   ========================================================= */

window.loadFinalCustomerProducts = async function () {
  try {
    const headers = {
      apikey: SUPABASE_KEY
    };

    const [productsResponse, variantsResponse, inventoryResponse] =
      await Promise.all([
        fetch(
          `${SUPABASE_URL}/rest/v1/products?select=id,category_id,name,slug,description,short_description,unit,is_active,is_featured&is_active=eq.true&order=name.asc`,
          { headers }
        ),

        fetch(
          `${SUPABASE_URL}/rest/v1/product_variants?select=id,product_id,name,sku,mrp,selling_price,is_active,quantity_value,quantity_unit&is_active=eq.true&order=name.asc`,
          { headers }
        ),

        fetch(
          `${SUPABASE_URL}/rest/v1/inventory?select=product_id,variant_id,stock_qty,reserved_qty,reorder_level&store_id=eq.7ef989c8-9826-437b-8a63-bb0dfa817540`,
          { headers }
        )
      ]);

    const products = await productsResponse.json();
    const variants = await variantsResponse.json();
    const inventory = await inventoryResponse.json();

    if (!productsResponse.ok ||
        !variantsResponse.ok ||
        !inventoryResponse.ok) {
      throw new Error("Products load failed.");
    }

    const productMap = {};
    products.forEach(product => {
      productMap[product.id] = product;
    });

    const inventoryMap = {};
    inventory.forEach(row => {
      inventoryMap[row.variant_id] = row;
    });

    const liveProducts = variants
      .map(variant => {
        const product =
          productMap[variant.product_id];

        if (!product) return null;

        const stock =
          inventoryMap[variant.id] || {};

        const available =
          Number(stock.stock_qty || 0) -
          Number(stock.reserved_qty || 0);

        if (available <= 0) {
          return null;
        }

        return {
          id: variant.id,
          product_id: variant.product_id,
          name: product.name,
          variant_name: variant.name,
          slug: product.slug,
          description: product.description,
          short_description:
            product.short_description,
          unit:
            variant.quantity_value &&
            variant.quantity_unit
              ? `${variant.quantity_value} ${variant.quantity_unit}`
              : (variant.name || product.unit || ""),
          mrp: Number(variant.mrp || 0),
          selling_price:
            Number(variant.selling_price || 0),
          price:
            Number(variant.selling_price || 0),
          stock: available,
          is_featured:
            product.is_featured === true
        };
      })
      .filter(Boolean);

    window.delyvoLiveProducts =
      liveProducts;

    window.allProducts =
      liveProducts;

    /*
     * Keep the existing customer renderer working.
     * Replace the global product list when it exists.
     */
    if (typeof window.renderProducts === "function") {
      window.renderProducts(
        liveProducts
      );
    }

    return liveProducts;

  } catch (error) {
    console.error(
      "FINAL CUSTOMER PRODUCT ERROR:",
      error
    );

    return [];
  }
};


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function () {
    setTimeout(function () {
      window.loadFinalCustomerProducts();
    }, 800);
  }
);


/* =========================================================
   DELYVO CUSTOMER - LIVE ORDER STATUS
   ========================================================= */

window.refreshDelyvoCustomerOrders = async function () {
  try {
    const token =
      localStorage.getItem("delyvo_access_token");

    if (!token) return;

    if (typeof window.openMyOrders === "function") {
      await window.openMyOrders();
    }

    if (
      window.delyvoCurrentOrderId &&
      typeof window.openDelyvoOrderDetails === "function"
    ) {
      await window.openDelyvoOrderDetails(
        window.delyvoCurrentOrderId
      );
    }

  } catch (error) {
    console.error(
      "CUSTOMER ORDER REFRESH ERROR:",
      error
    );
  }
};


/* ---------------------------------------------------------
   ORDER AUTO REFRESH
   --------------------------------------------------------- */

if (!window.delyvoCustomerOrderRefreshStarted) {

  window.delyvoCustomerOrderRefreshStarted = true;

  window.delyvoCustomerOrderRefreshInterval =
    setInterval(function () {

      const token =
        localStorage.getItem(
          "delyvo_access_token"
        );

      if (!token) return;

      /*
       * Only refresh when My Orders or Order Details
       * is currently visible.
       */
      const ordersModal =
        document.getElementById(
          "myOrdersModal"
        );

      const detailModal =
        document.getElementById(
          "delyvoOrderDetailsModal"
        );

      const ordersVisible =
        ordersModal &&
        getComputedStyle(ordersModal).display !== "none";

      const detailVisible =
        detailModal &&
        getComputedStyle(detailModal).display !== "none";

      if (ordersVisible || detailVisible) {
        window.refreshDelyvoCustomerOrders();
      }

    }, 20000);
}


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function () {

    /*
     * Keep customer order data fresh when the
     * account/order area is opened.
     */
    setTimeout(function () {

      const token =
        localStorage.getItem(
          "delyvo_access_token"
        );

      if (token) {
        window.delyvoCustomerLoggedIn = true;
      }

    }, 1000);

  }
);


/* =========================================================
   DELYVO CUSTOMER - FINAL AUTH SESSION
   ========================================================= */

window.getDelyvoAccessToken = async function () {
  let accessToken =
    localStorage.getItem("delyvo_access_token");

  const refreshToken =
    localStorage.getItem("delyvo_refresh_token");

  if (accessToken) {
    return accessToken;
  }

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(
      `${SUPABASE_URL}/auth/v1/token?grant_type=refresh_token`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: SUPABASE_KEY
        },
        body: JSON.stringify({
          refresh_token: refreshToken
        })
      }
    );

    const data = await response.json();

    if (!response.ok || !data.access_token) {
      localStorage.removeItem("delyvo_access_token");
      localStorage.removeItem("delyvo_refresh_token");
      return null;
    }

    localStorage.setItem(
      "delyvo_access_token",
      data.access_token
    );

    if (data.refresh_token) {
      localStorage.setItem(
        "delyvo_refresh_token",
        data.refresh_token
      );
    }

    return data.access_token;

  } catch (error) {
    console.error(
      "DELYVO SESSION REFRESH ERROR:",
      error
    );

    return null;
  }
};


/* ---------------------------------------------------------
   SESSION CHECK
   --------------------------------------------------------- */

window.checkDelyvoCustomerSession = async function () {

  const token =
    await window.getDelyvoAccessToken();

  if (!token) {
    window.delyvoCustomerLoggedIn = false;

    if (
      typeof window.updateLoginButton ===
      "function"
    ) {
      window.updateLoginButton();
    }

    return null;
  }

  try {

    const response = await fetch(
      `${SUPABASE_URL}/auth/v1/user`,
      {
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      localStorage.removeItem(
        "delyvo_access_token"
      );

      window.delyvoCustomerLoggedIn = false;

      if (
        typeof window.updateLoginButton ===
        "function"
      ) {
        window.updateLoginButton();
      }

      return null;
    }

    const user = await response.json();

    window.delyvoCustomerLoggedIn = true;
    window.delyvoCustomerUser = user;

    if (
      typeof window.updateLoginButton ===
      "function"
    ) {
      window.updateLoginButton();
    }

    return user;

  } catch (error) {
    console.error(
      "DELYVO SESSION CHECK ERROR:",
      error
    );

    return null;
  }
};


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function () {

    setTimeout(function () {
      window.checkDelyvoCustomerSession();
    }, 500);

  }
);


/* =========================================================
   DELYVO CUSTOMER - FINAL LIVE CATEGORIES
   ========================================================= */

window.loadFinalCustomerCategories = async function () {
  try {
    const response = await fetch(
      `${SUPABASE_URL}/rest/v1/categories?select=id,name,slug,image_url,is_active&is_active=eq.true&order=name.asc`,
      {
        headers: {
          apikey: SUPABASE_KEY
        }
      }
    );

    const categories = await response.json();

    if (!response.ok) {
      throw new Error("Categories load failed.");
    }

    window.delyvoLiveCategories =
      Array.isArray(categories)
        ? categories
        : [];

    window.allCategories =
      window.delyvoLiveCategories;

    if (
      typeof window.renderCategories ===
      "function"
    ) {
      window.renderCategories(
        window.delyvoLiveCategories
      );
    }

    return window.delyvoLiveCategories;

  } catch (error) {
    console.error(
      "FINAL CUSTOMER CATEGORY ERROR:",
      error
    );

    return [];
  }
};


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function () {
    setTimeout(function () {
      window.loadFinalCustomerCategories();
    }, 600);
  }
);

