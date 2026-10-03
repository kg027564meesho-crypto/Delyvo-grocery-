from pathlib import Path

p = Path("grocery/app.js")
js = p.read_text()

script = r'''
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

'''
# Insert before the last closing script tag.
pos = js.rfind("</script>")
if pos != -1:
    js = js[:pos] + script + js[pos:]
else:
    js += "\n<script>\n" + script + "\n</script>\n"

p.write_text(js)

print("FINAL CUSTOMER LIVE PRODUCTS CONNECTED")
