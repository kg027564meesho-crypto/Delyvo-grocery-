from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  function addProductFilters() {
    if (document.getElementById("shopProductFilters")) return;

    const productSection =
      document.querySelector("#productsSection") ||
      document.querySelector(".products-section");

    if (!productSection) return;

    const box = document.createElement("div");
    box.id = "shopProductFilters";

    box.innerHTML = `
      <div class="spf-row">
        <input
          id="shopProductSearch"
          type="search"
          placeholder="Search product..."
        >

        <select id="shopProductStatus">
          <option value="all">All Products</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="low">Low Stock</option>
        </select>
      </div>
    `;

    productSection.prepend(box);

    document
      .getElementById("shopProductSearch")
      .addEventListener("input", filterShopProducts);

    document
      .getElementById("shopProductStatus")
      .addEventListener("change", filterShopProducts);
  }

  function filterShopProducts() {
    const search =
      (
        document.getElementById("shopProductSearch")?.value ||
        ""
      ).toLowerCase().trim();

    const status =
      document.getElementById("shopProductStatus")?.value ||
      "all";

    document.querySelectorAll(
      "#productsSection tbody tr, .products-section tbody tr"
    ).forEach(row => {
      const text = row.textContent.toLowerCase();

      const matchesSearch =
        !search || text.includes(search);

      const activeButton =
        row.querySelector(
          ".product-active-toggle, .variant-active-toggle"
        );

      const isActive =
        activeButton?.dataset.active !== "false";

      const stockText =
        row.querySelector(
          ".stock-input, input[name*='stock'], input[type='number']"
        )?.value;

      const stock =
        Number(stockText || 0);

      let matchesStatus = true;

      if (status === "active") {
        matchesStatus = isActive;
      }

      if (status === "inactive") {
        matchesStatus = !isActive;
      }

      if (status === "low") {
        matchesStatus = stock <= 5;
      }

      row.style.display =
        matchesSearch && matchesStatus
          ? ""
          : "none";
    });
  }

  window.addShopProductFilters = addProductFilters;

  window.addEventListener("load", () => {
    setTimeout(addProductFilters, 500);
  });

  const style = document.createElement("style");

  style.textContent = `
    #shopProductFilters {
      margin:12px 0 18px;
    }

    .spf-row {
      display:flex;
      gap:10px;
      flex-wrap:wrap;
    }

    #shopProductSearch,
    #shopProductStatus {
      min-height:42px;
      padding:9px 12px;
      border:1px solid #ddd;
      border-radius:10px;
      background:#fff;
      font-size:14px;
      box-sizing:border-box;
    }

    #shopProductSearch {
      flex:1;
      min-width:220px;
    }

    #shopProductStatus {
      min-width:170px;
    }

    @media(max-width:600px) {
      #shopProductSearch,
      #shopProductStatus {
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
print("SHOP PRODUCT SEARCH + STATUS FILTER ADDED")
