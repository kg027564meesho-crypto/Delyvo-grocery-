from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

old = '''<button id="loginBtn" class="secondary-btn">Login</button>'''

new = '''<button id="myOrdersBtn" class="secondary-btn">My Orders</button>
  <button id="loginBtn" class="secondary-btn">Login</button>'''

if old in html and 'id="myOrdersBtn"' not in html:
    html = html.replace(old, new, 1)

script = r'''
<script>
(() => {
  function refreshOrdersButton() {
    const btn = document.getElementById("myOrdersBtn");
    if (!btn) return;

    btn.onclick = () => {
      if (!localStorage.getItem("delyvo_access_token")) {
        if (typeof window.openLogin === "function") {
          window.openLogin();
        } else {
          alert("Please login first.");
        }
        return;
      }

      if (typeof window.openMyOrders === "function") {
        window.openMyOrders();
      }
    };
  }

  refreshOrdersButton();

  window.refreshOrdersButton = refreshOrdersButton;
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("CUSTOMER MY ORDERS BUTTON ADDED")
