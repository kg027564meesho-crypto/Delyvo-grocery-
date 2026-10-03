from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  function addOrderFilters() {
    const section =
      document.querySelector("#ordersSection") ||
      document.querySelector(".orders-section");

    if (!section) return;

    if (document.getElementById("shopOrderFilters")) return;

    const box = document.createElement("div");
    box.id = "shopOrderFilters";

    box.innerHTML = `
      <div class="sof-row">
        <input
          id="shopOrderSearch"
          type="search"
          placeholder="Search order number or customer..."
        >

        <select id="shopOrderStatusFilter">
          <option value="all">All Orders</option>
          <option value="placed">New</option>
          <option value="confirmed">Confirmed</option>
          <option value="packing">Packing</option>
          <option value="packed">Ready</option>
          <option value="out_for_delivery">Out for Delivery</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    `;

    section.prepend(box);

    document
      .getElementById("shopOrderSearch")
      .addEventListener("input", filterShopOrders);

    document
      .getElementById("shopOrderStatusFilter")
      .addEventListener("change", filterShopOrders);
  }

  function filterShopOrders() {
    const search =
      (
        document.getElementById("shopOrderSearch")?.value ||
        ""
      ).toLowerCase().trim();

    const status =
      document.getElementById("shopOrderStatusFilter")?.value ||
      "all";

    document.querySelectorAll(".shop-order-card").forEach(card => {
      const text = card.textContent.toLowerCase();

      const matchesSearch =
        !search || text.includes(search);

      const cardStatus =
        card.dataset.status || "";

      const matchesStatus =
        status === "all" ||
        cardStatus === status;

      card.style.display =
        matchesSearch && matchesStatus
          ? ""
          : "none";
    });
  }

  window.addShopOrderFilters = addOrderFilters;

  window.addEventListener("load", () => {
    setTimeout(addOrderFilters, 400);
  });

  const oldLoad =
    window.loadShopOrders ||
    window.loadOrders;

  if (typeof oldLoad === "function") {
    const wrapped = async function() {
      const result = await oldLoad.apply(this, arguments);

      setTimeout(() => {
        addOrderFilters();
        filterShopOrders();
      }, 150);

      return result;
    };

    if (window.loadShopOrders) {
      window.loadShopOrders = wrapped;
    } else {
      window.loadOrders = wrapped;
    }
  }

  const style = document.createElement("style");

  style.textContent = `
    #shopOrderFilters {
      margin:12px 0 18px;
    }

    .sof-row {
      display:flex;
      gap:10px;
      flex-wrap:wrap;
    }

    #shopOrderSearch,
    #shopOrderStatusFilter {
      box-sizing:border-box;
      min-height:42px;
      padding:9px 12px;
      border:1px solid #ddd;
      border-radius:10px;
      background:#fff;
      font-size:14px;
    }

    #shopOrderSearch {
      flex:1;
      min-width:220px;
    }

    #shopOrderStatusFilter {
      min-width:170px;
    }

    @media(max-width:600px) {
      #shopOrderSearch,
      #shopOrderStatusFilter {
        width:100%;
        min-width:0;
      }
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
print("SHOP ORDER SEARCH + STATUS FILTER ADDED")
