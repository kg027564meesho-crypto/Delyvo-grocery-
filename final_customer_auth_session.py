from pathlib import Path

p = Path("grocery/app.js")
js = p.read_text()

script = r'''
/* =========================================================
   DELYVO CUSTOMER - FINAL AUTH SESSION
   ========================================================= */

window.getDelyvoAccessToken = async function () {
  let accessToken =
    localStorage.getItem("delyvo_access_token");

  const refreshToken =
    localStorage.getItem("delyvo_refresh_token");

  if (accessToken) {
    return accessToken;
  }

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(
      `${SUPABASE_URL}/auth/v1/token?grant_type=refresh_token`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: SUPABASE_KEY
        },
        body: JSON.stringify({
          refresh_token: refreshToken
        })
      }
    );

    const data = await response.json();

    if (!response.ok || !data.access_token) {
      localStorage.removeItem("delyvo_access_token");
      localStorage.removeItem("delyvo_refresh_token");
      return null;
    }

    localStorage.setItem(
      "delyvo_access_token",
      data.access_token
    );

    if (data.refresh_token) {
      localStorage.setItem(
        "delyvo_refresh_token",
        data.refresh_token
      );
    }

    return data.access_token;

  } catch (error) {
    console.error(
      "DELYVO SESSION REFRESH ERROR:",
      error
    );

    return null;
  }
};


/* ---------------------------------------------------------
   SESSION CHECK
   --------------------------------------------------------- */

window.checkDelyvoCustomerSession = async function () {

  const token =
    await window.getDelyvoAccessToken();

  if (!token) {
    window.delyvoCustomerLoggedIn = false;

    if (
      typeof window.updateLoginButton ===
      "function"
    ) {
      window.updateLoginButton();
    }

    return null;
  }

  try {

    const response = await fetch(
      `${SUPABASE_URL}/auth/v1/user`,
      {
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      localStorage.removeItem(
        "delyvo_access_token"
      );

      window.delyvoCustomerLoggedIn = false;

      if (
        typeof window.updateLoginButton ===
        "function"
      ) {
        window.updateLoginButton();
      }

      return null;
    }

    const user = await response.json();

    window.delyvoCustomerLoggedIn = true;
    window.delyvoCustomerUser = user;

    if (
      typeof window.updateLoginButton ===
      "function"
    ) {
      window.updateLoginButton();
    }

    return user;

  } catch (error) {
    console.error(
      "DELYVO SESSION CHECK ERROR:",
      error
    );

    return null;
  }
};


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

document.addEventListener(
  "DOMContentLoaded",
  function () {

    setTimeout(function () {
      window.checkDelyvoCustomerSession();
    }, 500);

  }
);

'''

pos = js.rfind("</script>")

if pos != -1:
    js = js[:pos] + script + js[pos:]
else:
    js += "\n<script>\n" + script + "\n</script>\n"

p.write_text(js)

print("FINAL CUSTOMER AUTH SESSION ADDED")
