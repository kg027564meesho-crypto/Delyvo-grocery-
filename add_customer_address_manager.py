from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const DLV_URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const DLV_KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  function token() {
    return localStorage.getItem("delyvo_access_token") || "";
  }

  async function addressApi(path, options = {}) {
    if (!token()) {
      throw new Error("Please login first.");
    }

    const response = await fetch(DLV_URL + path, {
      ...options,
      headers: {
        apikey: DLV_KEY,
        Authorization: "Bearer " + token(),
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(
        data?.message ||
        data?.msg ||
        data?.hint ||
        "Address request failed"
      );
    }

    return data;
  }

  async function openAddressManager() {
    let old = document.getElementById("delyvoAddressManager");
    if (old) old.remove();

    const modal = document.createElement("div");
    modal.id = "delyvoAddressManager";

    modal.innerHTML = `
      <div class="dam-backdrop"></div>

      <div class="dam-card">
        <div class="dam-head">
          <div>
            <h2>My Addresses</h2>
            <p>Select delivery address</p>
          </div>

          <button class="dam-close">×</button>
        </div>

        <div id="damList">
          Loading addresses...
        </div>

        <button id="damAdd" class="dam-add">
          + Add New Address
        </button>
      </div>
    `;

    document.body.appendChild(modal);

    modal.querySelector(".dam-close").onclick =
      () => modal.remove();

    modal.querySelector(".dam-backdrop").onclick =
      () => modal.remove();

    modal.querySelector("#damAdd").onclick = () => {
      showAddAddressForm();
    };

    await loadAddressList();
  }

  async function loadAddressList() {
    const list = document.getElementById("damList");
    if (!list) return;

    try {
      const addresses = await addressApi(
        "/rest/v1/addresses" +
        "?select=id,label,recipient_name,phone,address_line1,address_line2,landmark,city,state,pincode,is_default" +
        "&order=is_default.desc,created_at.desc"
      );

      if (!addresses.length) {
        list.innerHTML = `
          <div class="dam-empty">
            No saved address.
          </div>
        `;
        return;
      }

      list.innerHTML = addresses.map(address => `
        <div
          class="dam-address ${
            address.is_default ? "dam-default" : ""
          }"
        >
          <div>
            <strong>
              ${escapeHtml(address.label || "Address")}
            </strong>

            ${
              address.is_default
                ? `<span class="dam-badge">DEFAULT</span>`
                : ""
            }

            <p>
              ${escapeHtml(address.recipient_name || "")}
              ${
                address.phone
                  ? " · " + escapeHtml(address.phone)
                  : ""
              }
            </p>

            <p>
              ${escapeHtml(address.address_line1 || "")}
              ${
                address.address_line2
                  ? ", " + escapeHtml(address.address_line2)
                  : ""
              }
            </p>

            ${
              address.landmark
                ? `<p>Near ${escapeHtml(address.landmark)}</p>`
                : ""
            }

            <p>
              ${escapeHtml(address.city || "")},
              ${escapeHtml(address.state || "")}
              - ${escapeHtml(address.pincode || "")}
            </p>
          </div>

          <button
            class="dam-select"
            data-address-id="${address.id}"
          >
            ${
              address.is_default
                ? "Selected"
                : "Use This"
            }
          </button>
        </div>
      `).join("");

      list.querySelectorAll(".dam-select").forEach(button => {
        button.onclick = async () => {
          const id = button.dataset.addressId;

          const address =
            addresses.find(item => item.id === id);

          if (!address) return;

          localStorage.setItem(
            "delyvo_grocery_address",
            JSON.stringify(address)
          );

          document.getElementById("locationText").textContent =
            `${address.address_line1}, ${address.city}`;

          const modal =
            document.getElementById("delyvoAddressManager");

          if (modal) modal.remove();

          if (typeof window.openCheckout === "function") {
            window.openCheckout();
          }
        };
      });

    } catch (error) {
      list.innerHTML = `
        <div class="dam-error">
          ${escapeHtml(error.message)}
        </div>
      `;
    }
  }

  function showAddAddressForm() {
    const list = document.getElementById("damList");
    if (!list) return;

    list.innerHTML = `
      <form id="damForm" class="dam-form">
        <input name="label" placeholder="Label (Home / Work)" required>
        <input name="recipient_name" placeholder="Your Name" required>
        <input name="phone" placeholder="Phone Number" required>
        <input name="address_line1" placeholder="Address" required>
        <input name="address_line2" placeholder="Area / Street">
        <input name="landmark" placeholder="Landmark">
        <input name="city" value="Modinagar" placeholder="City" required>
        <input name="state" value="Uttar Pradesh" placeholder="State">
        <input name="pincode" value="201204" placeholder="Pincode" required>

        <label class="dam-default-check">
          <input type="checkbox" name="is_default" checked>
          Make this default address
        </label>

        <button type="submit" class="dam-save">
          Save Address
        </button>

        <button type="button" id="damCancel" class="dam-cancel">
          Cancel
        </button>

        <p id="damMessage"></p>
      </form>
    `;

    document.getElementById("damCancel").onclick =
      loadAddressList;

    document.getElementById("damForm").onsubmit =
      async event => {
        event.preventDefault();

        const form = event.currentTarget;
        const message =
          document.getElementById("damMessage");

        const data = Object.fromEntries(
          new FormData(form).entries()
        );

        const payload = {
          label: data.label,
          recipient_name: data.recipient_name,
          phone: data.phone,
          address_line1: data.address_line1,
          address_line2: data.address_line2 || null,
          landmark: data.landmark || null,
          city: data.city,
          state: data.state || "Uttar Pradesh",
          pincode: data.pincode,
          is_default: form.is_default.checked
        };

        try {
          message.textContent = "Saving...";

          if (payload.pincode !== "201204") {
            throw new Error(
              "Abhi Delyvo delivery area sirf Modinagar 201204 hai."
            );
          }

          await addressApi(
            "/rest/v1/addresses",
            {
              method: "POST",
              headers: {
                Prefer: "return=representation"
              },
              body: JSON.stringify(payload)
            }
          );

          message.textContent =
            "Address saved successfully.";

          await loadAddressList();

        } catch (error) {
          message.textContent =
            error.message || "Address save failed.";
        }
      };
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.openAddressManager = openAddressManager;

  const locationButton =
    document.getElementById("locationBtn");

  if (locationButton) {
    locationButton.onclick = async () => {
      if (!token()) {
        if (typeof window.openLogin === "function") {
          window.openLogin();
        }
        return;
      }

      await openAddressManager();
    };
  }

  const style = document.createElement("style");

  style.textContent = `
    #delyvoAddressManager {
      position:fixed;
      inset:0;
      z-index:99996;
    }

    .dam-backdrop {
      position:absolute;
      inset:0;
      background:rgba(0,0,0,.55);
    }

    .dam-card {
      position:relative;
      z-index:2;
      width:min(94%,620px);
      max-height:88vh;
      overflow:auto;
      margin:5vh auto 0;
      padding:20px;
      background:#fff;
      border-radius:20px;
      box-shadow:0 15px 50px rgba(0,0,0,.25);
    }

    .dam-head {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      margin-bottom:18px;
    }

    .dam-head h2 {
      margin:0;
    }

    .dam-head p {
      margin:4px 0 0;
      color:#777;
    }

    .dam-close {
      width:38px;
      height:38px;
      border:0;
      border-radius:50%;
      background:#f2f2f2;
      font-size:24px;
      cursor:pointer;
    }

    .dam-address {
      display:flex;
      justify-content:space-between;
      gap:12px;
      padding:14px;
      margin-bottom:10px;
      border:1px solid #ddd;
      border-radius:12px;
    }

    .dam-default {
      border-width:2px;
    }

    .dam-address p {
      margin:5px 0;
      color:#666;
      font-size:13px;
    }

    .dam-badge {
      display:inline-block;
      margin-left:6px;
      padding:3px 6px;
      border-radius:5px;
      background:#eee;
      font-size:9px;
      font-weight:800;
    }

    .dam-select,
    .dam-add,
    .dam-save,
    .dam-cancel {
      padding:9px 12px;
      border-radius:9px;
      cursor:pointer;
      font-weight:700;
    }

    .dam-select {
      height:max-content;
      border:1px solid #ddd;
      background:#fff;
    }

    .dam-add,
    .dam-save {
      width:100%;
      border:0;
      background:#111;
      color:#fff;
      margin-top:12px;
    }

    .dam-cancel {
      width:100%;
      border:1px solid #ddd;
      background:#fff;
      margin-top:8px;
    }

    .dam-form {
      display:grid;
      gap:9px;
    }

    .dam-form input:not([type="checkbox"]) {
      box-sizing:border-box;
      width:100%;
      padding:11px;
      border:1px solid #ddd;
      border-radius:9px;
    }

    .dam-default-check {
      font-size:13px;
      color:#555;
    }

    .dam-empty,
    .dam-error {
      text-align:center;
      padding:25px;
      color:#777;
    }

    .dam-error {
      color:#b00020;
    }

    #damMessage {
      text-align:center;
      font-size:13px;
    }

    @media(max-width:600px) {
      .dam-card {
        width:96%;
        margin-top:3vh;
        padding:16px;
      }

      .dam-address {
        flex-direction:column;
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
print("CUSTOMER MULTI ADDRESS MANAGER ADDED")
