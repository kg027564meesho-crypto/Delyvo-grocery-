from pathlib import Path

p = Path("grocery/app.js")
html = p.read_text()

script = r'''
<script>
/* Delyvo: final customer address save */
window.saveAddressToDatabase = async function(address) {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Pehle customer login karein.");
  }

  const user = await getAuthUser();

  if (!user || !user.id) {
    throw new Error("Customer session nahi mili. Dobara login karein.");
  }

  if (String(address.pincode).trim() !== "201204") {
    throw new Error("Abhi Delyvo delivery sirf Modinagar 201204 mein available hai.");
  }

  const payload = {
    user_id: user.id,
    label: address.label || "Home",
    recipient_name: address.recipient_name || "",
    phone: address.phone || "",
    address_line1: address.address_line1 || "",
    address_line2: address.address_line2 || null,
    landmark: address.landmark || null,
    city: address.city || "Modinagar",
    state: address.state || "Uttar Pradesh",
    pincode: String(address.pincode).trim(),
    latitude: address.latitude || null,
    longitude: address.longitude || null,
    is_default: !!address.is_default
  };

  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/addresses`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${token}`,
        Prefer: "return=representation"
      },
      body: JSON.stringify(payload)
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message ||
      data.hint ||
      data.details ||
      "Address save nahi ho paya."
    );
  }

  const saved = Array.isArray(data) ? data[0] : data;

  if (saved && saved.id) {
    localStorage.setItem(
      "delyvo_grocery_address",
      JSON.stringify(saved)
    );
  }

  return saved;
};
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", script + "\n</body>", 1)
else:
    html += script

p.write_text(html)

print("CUSTOMER ADDRESS USER ID FIXED")
