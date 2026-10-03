from pathlib import Path

p = Path("grocery/app.js")
js = p.read_text()

script = r'''
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

'''

pos = js.rfind("</script>")

if pos != -1:
    js = js[:pos] + script + js[pos:]
else:
    js += "\n<script>\n" + script + "\n</script>\n"

p.write_text(js)

print("FINAL CUSTOMER LIVE CATEGORIES CONNECTED")
