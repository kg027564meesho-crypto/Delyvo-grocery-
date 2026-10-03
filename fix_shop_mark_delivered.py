from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const DLV_SUPABASE_URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const DLV_SUPABASE_KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  function shopToken() {
    return localStorage.getItem("delyvo_shop_token") || "";
  }

  async function shopRequest(path, options = {}) {
    const response = await fetch(
      DLV_SUPABASE_URL + path,
      {
        ...options,
        headers: {
          apikey: DLV_SUPABASE_KEY,
          Authorization: "Bearer " + shopToken(),
          "Content-Type": "application/json",
          ...(options.headers || {})
        }
      }
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(
        data?.message ||
        data?.msg ||
        data?.hint ||
        "Shop request failed"
      );
    }

    return data;
  }

  async function markShopOrderDelivered(orderId) {
    if (!orderId) return;

    if (!shopToken()) {
      alert("Shop login required.");
      return;
    }

    try {
      const deliveries = await shopRequest(
        "/rest/v1/deliveries" +
        "?select=id,status,order_id" +
        "&order_id=eq." + encodeURIComponent(orderId) +
        "&limit=1"
      );

      if (!deliveries || !deliveries.length) {
        throw new Error(
          "Delivery record nahi mila. Pehle order ko Out for Delivery karo."
        );
      }

      const delivery = deliveries[0];

      await shopRequest(
        "/rest/v1/deliveries?id=eq." +
        encodeURIComponent(delivery.id),
        {
          method: "PATCH",
          body: JSON.stringify({
            status: "delivered",
            delivered_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
        }
      );

      await shopRequest(
        "/rest/v1/rpc/transition_order_status",
        {
          method: "POST",
          body: JSON.stringify({
            p_order_id: orderId,
            p_new_status: "delivered"
          })
        }
      );

      alert("Order delivered successfully.");

      if (typeof window.loadShopOrders === "function") {
        await window.loadShopOrders();
      } else if (typeof window.loadOrders === "function") {
        await window.loadOrders();
      } else {
        location.reload();
      }

    } catch (error) {
      alert(error.message || "Order delivery update failed.");
    }
  }

  window.markShopOrderDelivered = markShopOrderDelivered;
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

# Existing delivered button ko new workflow se connect karna
html = html.replace(
    'onclick="updateShopOrderStatus(\'${order.id}\', \'delivered\')"',
    'onclick="markShopOrderDelivered(\'${order.id}\')"'
)

html = html.replace(
    'onclick="updateOrderStatus(\'${order.id}\', \'delivered\')"',
    'onclick="markShopOrderDelivered(\'${order.id}\')"'
)

p.write_text(html)
print("SHOP MARK DELIVERED WORKFLOW FIXED")
