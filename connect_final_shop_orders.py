from pathlib import Path
import re

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
/* =========================================================
   DELYVO - CONNECT FINAL SHOP ORDER RENDERER
   ========================================================= */

window.connectFinalShopOrderLoader = function () {

  if (typeof window.loadShopOrders !== "function") {
    return;
  }

  if (window.__delyvoFinalShopLoaderConnected) {
    return;
  }

  const originalLoadShopOrders =
    window.loadShopOrders;

  window.loadShopOrders = async function () {

    try {

      const result =
        await originalLoadShopOrders.apply(
          this,
          arguments
        );

      /*
       * Existing loader may already render its own list.
       * Fetch the complete order data again so the final
       * renderer always receives customer/address/items.
       */

      const token =
        localStorage.getItem(
          "delyvo_shop_token"
        );

      if (!token) {
        return result;
      }

      const response =
        await fetch(
          `${SHOP_SUPABASE_URL}/rest/v1/orders?select=id,order_number,status,payment_status,subtotal,delivery_fee,total,created_at,address_id,order_items(id,product_name,variant_name,quantity,unit_price,total),addresses(recipient_name,phone,address_line1,address_line2,landmark,city,state,pincode)&order=created_at.desc`,
          {
            headers: {
              apikey: SHOP_SUPABASE_KEY,
              Authorization:
                `Bearer ${token}`
            }
          }
        );

      if (!response.ok) {
        return result;
      }

      const orders =
        await response.json();

      if (
        typeof window.renderFinalShopOrders ===
        "function"
      ) {
        window.renderFinalShopOrders(
          Array.isArray(orders)
            ? orders
            : []
        );

        if (
          typeof window.filterFinalShopOrders ===
          "function"
        ) {
          window.filterFinalShopOrders();
        }
      }

      return result;

    } catch (error) {

      console.error(
        "FINAL SHOP ORDER CONNECTION ERROR:",
        error
      );

    }
  };

  window.__delyvoFinalShopLoaderConnected =
    true;
};


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function () {

    setTimeout(function () {

      window.connectFinalShopOrderLoader();

      /*
       * Connect once more after existing page scripts
       * have finished defining their functions.
       */
      setTimeout(
        window.connectFinalShopOrderLoader,
        1200
      );

    }, 1200);

  }
);

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

print("FINAL SHOP ORDER LOADER CONNECTED")
