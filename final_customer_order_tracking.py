from pathlib import Path

p = Path("grocery/app.js")
js = p.read_text()

script = r'''
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

'''

pos = js.rfind("</script>")

if pos != -1:
    js = js[:pos] + script + js[pos:]
else:
    js += "\n<script>\n" + script + "\n</script>\n"

p.write_text(js)

print("FINAL CUSTOMER LIVE ORDER TRACKING ADDED")
