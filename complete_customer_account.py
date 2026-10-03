from pathlib import Path

p = Path("grocery/index.html")
html = p.read_text()

script = r'''
<script>
(() => {
  const DLV_URL = "https://unwdkreujyejgcucgttj.supabase.co";
  const DLV_KEY = "sb_publishable_QylVZHuaIj98axBkNuvbFA_Z6NX-9Q6";

  function customerToken() {
    return localStorage.getItem("delyvo_access_token") || "";
  }

  function clearCustomerSession() {
    localStorage.removeItem("delyvo_access_token");
    localStorage.removeItem("delyvo_refresh_token");
  }

  async function currentCustomer() {
    const token = customerToken();
    if (!token) return null;

    try {
      const response = await fetch(DLV_URL + "/auth/v1/user", {
        headers: {
          apikey: DLV_KEY,
          Authorization: "Bearer " + token
        }
      });

      if (!response.ok) {
        clearCustomerSession();
        return null;
      }

      return await response.json();
    } catch {
      return null;
    }
  }

  function showAccount() {
    let modal = document.getElementById("delyvoAccountModal");

    if (!modal) {
      modal = document.createElement("div");
      modal.id = "delyvoAccountModal";

      modal.innerHTML = `
        <div class="da-backdrop"></div>

        <div class="da-card">
          <div class="da-head">
            <div>
              <h2>My Account</h2>
              <p>Delyvo Customer</p>
            </div>

            <button class="da-close">×</button>
          </div>

          <div class="da-email" id="daEmail">
            Loading...
          </div>

          <button class="da-orders">My Orders</button>
          <button class="da-logout">Logout</button>
        </div>
      `;

      document.body.appendChild(modal);

      modal.querySelector(".da-close").onclick =
        () => modal.remove();

      modal.querySelector(".da-backdrop").onclick =
        () => modal.remove();

      modal.querySelector(".da-orders").onclick = () => {
        modal.remove();

        if (typeof window.openMyOrders === "function") {
          window.openMyOrders();
        }
      };

      modal.querySelector(".da-logout").onclick = () => {
        clearCustomerSession();
        modal.remove();
        updateCustomerAccountButton();
        alert("Logout successful.");
      };
    }

    currentCustomer().then(user => {
      const email = user?.email || "Customer";
      const emailBox = document.getElementById("daEmail");

      if (emailBox) {
        emailBox.textContent = email;
      }
    });
  }

  function updateCustomerAccountButton() {
    const loginBtn = document.getElementById("loginBtn");

    if (!loginBtn) return;

    if (customerToken()) {
      loginBtn.textContent = "Account";
      loginBtn.classList.add("customer-logged-in");

      loginBtn.onclick = showAccount;
    } else {
      loginBtn.textContent = "Login";
      loginBtn.classList.remove("customer-logged-in");

      loginBtn.onclick = () => {
        if (typeof window.openLogin === "function") {
          window.openLogin();
        }
      };
    }
  }

  window.customerLogout = () => {
    clearCustomerSession();
    updateCustomerAccountButton();
  };

  // Existing auth form ko login ke saath connect karna
  const authForm = document.getElementById("authForm");

  if (authForm) {
    authForm.addEventListener("submit", async event => {
      event.preventDefault();

      const email =
        document.getElementById("authEmail")?.value.trim();

      const password =
        document.getElementById("authPassword")?.value;

      const message =
        document.getElementById("authMessage");

      if (!email || !password) {
        if (message) {
          message.textContent =
            "Email aur password required hai.";
        }
        return;
      }

      try {
        if (message) {
          message.textContent = "Login ho raha hai...";
        }

        if (typeof window.authLogin !== "function") {
          throw new Error("Login system unavailable.");
        }

        await window.authLogin(email, password);

        if (message) {
          message.textContent = "Login successful.";
        }

        updateCustomerAccountButton();

        setTimeout(() => {
          const modal =
            document.getElementById("authModal");

          if (modal) modal.style.display = "none";
        }, 400);

      } catch (error) {
        if (message) {
          message.textContent =
            error.message || "Login failed.";
        }
      }
    });
  }

  // Signup
  const signupBtn = document.getElementById("signupBtn");

  if (signupBtn) {
    signupBtn.addEventListener("click", async () => {
      const email =
        document.getElementById("authEmail")?.value.trim();

      const password =
        document.getElementById("authPassword")?.value;

      const message =
        document.getElementById("authMessage");

      if (!email || !password) {
        if (message) {
          message.textContent =
            "Signup ke liye email aur password bharo.";
        }
        return;
      }

      if (password.length < 6) {
        if (message) {
          message.textContent =
            "Password kam se kam 6 characters ka hona chahiye.";
        }
        return;
      }

      try {
        if (message) {
          message.textContent = "Account create ho raha hai...";
        }

        if (typeof window.authSignup !== "function") {
          throw new Error("Signup system unavailable.");
        }

        const result =
          await window.authSignup(email, password);

        if (result?.access_token) {
          localStorage.setItem(
            "delyvo_access_token",
            result.access_token
          );

          if (result.refresh_token) {
            localStorage.setItem(
              "delyvo_refresh_token",
              result.refresh_token
            );
          }

          updateCustomerAccountButton();

          if (message) {
            message.textContent =
              "Account created successfully.";
          }

          setTimeout(() => {
            const modal =
              document.getElementById("authModal");

            if (modal) modal.style.display = "none";
          }, 500);
        } else {
          if (message) {
            message.textContent =
              "Account create ho gaya. Agar email confirmation maange to email confirm karo, phir login karo.";
          }
        }

      } catch (error) {
        if (message) {
          message.textContent =
            error.message || "Signup failed.";
        }
      }
    });
  }

  // Existing Login button
  const loginBtn = document.getElementById("loginBtn");

  if (loginBtn) {
    loginBtn.onclick = () => {
      if (customerToken()) {
        showAccount();
      } else if (typeof window.openLogin === "function") {
        window.openLogin();
      }
    };
  }

  const style = document.createElement("style");

  style.textContent = `
    .customer-logged-in {
      font-weight:700;
    }

    #delyvoAccountModal {
      position:fixed;
      inset:0;
      z-index:99998;
    }

    .da-backdrop {
      position:absolute;
      inset:0;
      background:rgba(0,0,0,.55);
    }

    .da-card {
      position:relative;
      z-index:2;
      width:min(92%,430px);
      margin:10vh auto 0;
      padding:22px;
      background:#fff;
      border-radius:20px;
      box-shadow:0 15px 50px rgba(0,0,0,.25);
    }

    .da-head {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      margin-bottom:20px;
    }

    .da-head h2 {
      margin:0;
    }

    .da-head p {
      margin:4px 0 0;
      color:#777;
    }

    .da-close {
      width:38px;
      height:38px;
      border:0;
      border-radius:50%;
      background:#f2f2f2;
      font-size:24px;
      cursor:pointer;
    }

    .da-email {
      padding:14px;
      border-radius:10px;
      background:#f5f5f5;
      margin-bottom:15px;
      word-break:break-word;
      font-weight:600;
    }

    .da-orders,
    .da-logout {
      width:100%;
      padding:12px;
      margin-top:9px;
      border-radius:10px;
      cursor:pointer;
      font-weight:700;
    }

    .da-orders {
      border:1px solid #ddd;
      background:#fff;
    }

    .da-logout {
      border:0;
      background:#111;
      color:#fff;
    }
  `;

  document.head.appendChild(style);

  updateCustomerAccountButton();
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)
print("CUSTOMER ACCOUNT LOGIN SIGNUP LOGOUT COMPLETED")
