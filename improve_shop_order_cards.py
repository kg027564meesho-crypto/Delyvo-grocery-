from pathlib import Path

p = Path("grocery/shop.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const style = document.createElement("style");

  style.textContent = `
    .shop-order-card {
      background:#fff;
      border:1px solid #e5e5e5;
      border-radius:16px;
      padding:16px;
      margin-bottom:14px;
      box-shadow:0 3px 12px rgba(0,0,0,.05);
    }

    .shop-order-top {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:12px;
      margin-bottom:12px;
    }

    .shop-order-number {
      font-weight:800;
      font-size:16px;
    }

    .shop-order-date {
      color:#777;
      font-size:12px;
      margin-top:3px;
    }

    .shop-order-status {
      padding:6px 9px;
      border-radius:8px;
      background:#f1f1f1;
      font-size:11px;
      font-weight:800;
      white-space:nowrap;
    }

    .shop-customer-box {
      background:#f8f8f8;
      border-radius:11px;
      padding:11px;
      margin-bottom:12px;
    }

    .shop-customer-box strong {
      display:block;
      margin-bottom:4px;
    }

    .shop-customer-box span {
      display:block;
      color:#666;
      font-size:13px;
      margin-top:2px;
    }

    .shop-order-items {
      border-top:1px solid #eee;
      border-bottom:1px solid #eee;
      padding:10px 0;
      margin-bottom:12px;
    }

    .shop-order-item {
      display:flex;
      justify-content:space-between;
      gap:10px;
      padding:5px 0;
      font-size:13px;
    }

    .shop-order-total {
      display:flex;
      justify-content:space-between;
      font-size:17px;
      font-weight:800;
      margin-bottom:12px;
    }

    .shop-order-actions {
      display:flex;
      flex-wrap:wrap;
      gap:8px;
    }

    .shop-order-actions button {
      padding:9px 12px;
      border:1px solid #ddd;
      border-radius:9px;
      background:#fff;
      font-weight:700;
      cursor:pointer;
    }

    .shop-order-actions button:hover {
      background:#f5f5f5;
    }

    .shop-order-actions .danger {
      color:#b00020;
    }

    .shop-order-empty {
      padding:30px 15px;
      text-align:center;
      color:#777;
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
print("SHOP ORDER CARD UI ADDED")
