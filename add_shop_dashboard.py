from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  function shopToken() {
    return localStorage.getItem("delyvo_shop_token") || "";
  }

  async function dashboardApi(path) {
    const r = await fetch(URL + path, {
      headers: {
        apikey: KEY,
        Authorization: "Bearer " + shopToken()
      }
    });

    const data = await r.json().catch(() => []);
    if (!r.ok) throw new Error(data?.message || "Dashboard request failed");
    return data;
  }

  async function loadDashboardStats() {
    const stats = document.getElementById("delyvoDashboardStats");
    if (!stats || !shopToken()) return;

    try {
      const orders = await dashboardApi(
        "/rest/v1/orders?select=id,status,total,created_at"
      );

      const products = await dashboardApi(
        "/rest/v1/product_variants?select=id,is_active"
      );

      const inventory = await dashboardApi(
        "/rest/v1/inventory?select=id,stock_qty,reorder_level"
      );

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const todayOrders = orders.filter(o =>
        new Date(o.created_at) >= today
      );

      const pending = orders.filter(o =>
        ["placed", "pending"].includes(o.status)
      ).length;

      const preparing = orders.filter(o =>
        ["confirmed", "packing", "packed"].includes(o.status)
      ).length;

      const delivery = orders.filter(o =>
        ["out_for_delivery"].includes(o.status)
      ).length;

      const lowStock = inventory.filter(i =>
        Number(i.stock_qty || 0) <= Number(i.reorder_level || 5)
      ).length;

      const activeProducts = products.filter(p => p.is_active).length;

      const salesToday = todayOrders.reduce(
        (sum, o) => sum + Number(o.total || 0),
        0
      );

      stats.innerHTML = `
        <div class="db-card">
          <span>Today's Orders</span>
          <strong>${todayOrders.length}</strong>
        </div>

        <div class="db-card">
          <span>Pending</span>
          <strong>${pending}</strong>
        </div>

        <div class="db-card">
          <span>Preparing</span>
          <strong>${preparing}</strong>
        </div>

        <div class="db-card">
          <span>Out for Delivery</span>
          <strong>${delivery}</strong>
        </div>

        <div class="db-card">
          <span>Today's Sales</span>
          <strong>₹${salesToday.toFixed(0)}</strong>
        </div>

        <div class="db-card">
          <span>Low Stock</span>
          <strong>${lowStock}</strong>
        </div>

        <div class="db-card">
          <span>Active Products</span>
          <strong>${activeProducts}</strong>
        </div>
      `;

    } catch (e) {
      stats.innerHTML =
        "<div class='db-error'>Dashboard data load nahi hua.</div>";
    }
  }

  function addDashboard() {
    if (document.getElementById("delyvoDashboard")) return;

    const dashboard = document.createElement("section");
    dashboard.id = "delyvoDashboard";

    dashboard.innerHTML = `
      <div class="db-head">
        <div>
          <h1>Delyvo Grocery</h1>
          <p>Shop Dashboard</p>
        </div>

        <button id="dbRefresh">Refresh Dashboard</button>
      </div>

      <div id="delyvoDashboardStats" class="db-grid">
        <div class="db-loading">Loading dashboard...</div>
      </div>
    `;

    document.body.insertBefore(
      dashboard,
      document.body.firstChild
    );

    document.getElementById("dbRefresh").onclick =
      loadDashboardStats;
  }

  function addDashboardStyle() {
    const style = document.createElement("style");

    style.textContent = `
      #delyvoDashboard {
        max-width:1100px;
        margin:20px auto 0;
        padding:20px;
        background:#fff;
        border-radius:18px;
        box-shadow:0 4px 22px rgba(0,0,0,.08);
      }

      .db-head {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:20px;
        margin-bottom:20px;
      }

      .db-head h1 {
        margin:0;
        font-size:26px;
      }

      .db-head p {
        margin:4px 0 0;
        color:#777;
      }

      #dbRefresh {
        border:0;
        padding:11px 16px;
        border-radius:9px;
        background:#111;
        color:#fff;
        cursor:pointer;
      }

      .db-grid {
        display:grid;
        grid-template-columns:
          repeat(4, minmax(0, 1fr));
        gap:12px;
      }

      .db-card {
        min-height:95px;
        padding:16px;
        border:1px solid #eee;
        border-radius:14px;
        background:#fafafa;
        box-sizing:border-box;
      }

      .db-card span {
        display:block;
        color:#666;
        font-size:13px;
        margin-bottom:9px;
      }

      .db-card strong {
        font-size:25px;
      }

      .db-loading,
      .db-error {
        padding:20px;
        color:#777;
      }

      .db-error {
        color:#b00020;
      }

      @media(max-width:850px) {
        .db-grid {
          grid-template-columns:
            repeat(2, minmax(0, 1fr));
        }
      }

      @media(max-width:520px) {
        #delyvoDashboard {
          margin:10px;
          padding:14px;
        }

        .db-head {
          align-items:flex-start;
          flex-direction:column;
        }

        .db-grid {
          grid-template-columns:1fr;
        }

        #dbRefresh {
          width:100%;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function startDashboard() {
    addDashboardStyle();
    addDashboard();
    loadDashboardStats();
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      startDashboard
    );
  } else {
    startDashboard();
  }
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("SHOP DASHBOARD ADDED")
