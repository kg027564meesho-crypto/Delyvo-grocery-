from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const DLV_URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const DLV_KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  function shopToken() {
    return localStorage.getItem("delyvo_shop_token") || "";
  }

  async function rejectShopOrder(orderId) {
    if (!orderId) return;

    if (!shopToken()) {
      alert("Shop login required.");
      return;
    }

    const ok = confirm(
      "Kya aap is order ko reject/cancel karna chahte ho?"
    );

    if (!ok) return;

    try {
      const response = await fetch(
        DLV_URL + "/rest/v1/rpc/transition_order_status",
        {
          method: "POST",
          headers: {
            apikey: DLV_KEY,
            Authorization: "Bearer " + shopToken(),
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            p_order_id: orderId,
            p_new_status: "cancelled"
          })
        }
      );

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.message ||
          data?.msg ||
          data?.hint ||
          "Order reject failed"
        );
      }

      alert("Order rejected successfully.");

      if (typeof window.loadShopOrders === "function") {
        await window.loadShopOrders();
      } else if (typeof window.loadOrders === "function") {
        await window.loadOrders();
      } else {
        location.reload();
      }

    } catch (error) {
      alert(error.message || "Order reject failed.");
    }
  }

  window.rejectShopOrder = rejectShopOrder;

  // Existing Accept button ke paas Reject button add karna
  function addRejectButtons() {
    document.querySelectorAll("[data-order-id]").forEach(row => {
      const orderId = row.getAttribute("data-order-id");
      if (!orderId) return;

      if (row.querySelector(".dlv-reject-order")) return;

      const acceptButton =
        row.querySelector("button");

      if (!acceptButton) return;

      const button = document.createElement("button");
      button.className = "dlv-reject-order";
      button.textContent = "Reject Order";

      button.onclick = () => rejectShopOrder(orderId);

      acceptButton.parentNode.appendChild(button);
    });
  }

  window.addEventListener("load", () => {
    setTimeout(addRejectButtons, 500);
  });

  const oldLoadShopOrders = window.loadShopOrders;

  if (typeof oldLoadShopOrders === "function") {
    window.loadShopOrders = async function() {
      const result = await oldLoadShopOrders();
      setTimeout(addRejectButtons, 150);
      return result;
    };
  }

  const oldLoadOrders = window.loadOrders;

  if (typeof oldLoadOrders === "function") {
    window.loadOrders = async function() {
      const result = await oldLoadOrders();
      setTimeout(addRejectButtons, 150);
      return result;
    };
  }

  const style = document.createElement("style");

  style.textContent = `
    .dlv-reject-order {
      margin-left:8px;
      padding:8px 12px;
      border:1px solid #ddd;
      border-radius:8px;
      background:#fff;
      color:#b00020;
      font-weight:700;
      cursor:pointer;
    }

    .dlv-reject-order:hover {
      background:#fff1f1;
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
print("SHOP REJECT ORDER ADDED")
