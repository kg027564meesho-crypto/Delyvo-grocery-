from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  let shopRefreshTimer = null;

  function startShopAutoRefresh() {
    if (shopRefreshTimer) {
      clearInterval(shopRefreshTimer);
    }

    shopRefreshTimer = setInterval(async () => {
      if (!localStorage.getItem("delyvo_shop_token")) {
        return;
      }

      try {
        if (typeof window.loadShopOrders === "function") {
          await window.loadShopOrders();
        } else if (typeof window.loadOrders === "function") {
          await window.loadOrders();
        }

        if (typeof window.loadShopDashboard === "function") {
          await window.loadShopDashboard();
        }
      } catch (error) {
        console.log("Shop auto refresh:", error.message);
      }
    }, 30000);
  }

  window.startShopAutoRefresh = startShopAutoRefresh;

  window.addEventListener("load", () => {
    setTimeout(startShopAutoRefresh, 1500);
  });

  const style = document.createElement("style");

  style.textContent = `
    .shop-refresh-info {
      margin:8px 0 14px;
      padding:8px 11px;
      border-radius:8px;
      background:#f5f5f5;
      color:#666;
      font-size:12px;
    }
  `;

  document.head.appendChild(style);

  const info = document.createElement("div");
  info.className = "shop-refresh-info";
  info.textContent = "Orders automatically refresh every 30 seconds.";

  const ordersSection =
    document.querySelector("#ordersSection") ||
    document.querySelector(".orders-section");

  if (ordersSection) {
    ordersSection.prepend(info);
  }
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)

print("SHOP AUTO REFRESH ADDED")
