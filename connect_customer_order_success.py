from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const oldPlaceOrder = window.placeOrder;

  if (typeof oldPlaceOrder !== "function") {
    console.log("PLACE ORDER FUNCTION NOT FOUND - SUCCESS HOOK ADDED FOR LATER");
    return;
  }

  window.placeOrder = async function() {
    try {
      const result = await oldPlaceOrder.apply(this, arguments);

      if (result && typeof window.showDelyvoOrderSuccess === "function") {
        window.showDelyvoOrderSuccess(result);
      }

      return result;
    } catch (error) {
      throw error;
    }
  };

  console.log("CUSTOMER ORDER SUCCESS CONNECTED");
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("CUSTOMER ORDER SUCCESS CONNECTED")
