
from flask import Flask, render_template_string, request, redirect, make_response
import os

app = Flask(__name__)

merchant_data = {
    "abc123": {
        "merchant_name": "DanielPay Vending",
        "amount": "0.01",
        "email": "d.saindon09@gmail.com"
    }
}

bank_list = [
    {"name": "TD", "url": "td"},
    {"name": "KOHO", "url": "koho"},
    {"name": "DUCA", "url": "https://www.duca.com"}
]

@app.route("/pay/<ref>")
def pay(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>DanielPay | Confirm Payment</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
        body { font-family: Arial; text-align: center; padding: 40px; }
        .box { border: 1px solid #ccc; padding: 20px; border-radius: 10px; max-width: 400px; margin: auto; }
        button { padding: 10px 20px; background-color: #0070f3; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
    </style>
</head>
<body>
    <div class='box'>
        <h2>Pay {{ merchant['merchant_name'] }}</h2>
        <p>You're about to send <strong>${{ merchant['amount'] }}</strong>.</p>
        <form action='/select_bank/{{ ref }}' method='get'>
            <button type='submit'>Yes, Send via My Bank</button>
        </form>
    </div>
</body>
</html>
""", merchant=merchant, ref=ref)

@app.route("/select_bank/<ref>")
def select_bank(ref):
    previous = request.cookies.get("danielpay_bank")
    previous_bank = next((b for b in bank_list if b["url"] == previous), None)

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Select Bank | DanielPay</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
        body { font-family: Arial; padding: 20px; text-align: center; }
        input { width: 90%; padding: 10px; font-size: 16px; margin-bottom: 20px; }
        ul { list-style: none; padding: 0; max-height: 300px; overflow-y: auto; }
        li { margin: 8px 0; }
        button { font-size: 16px; padding: 8px 14px; background-color: #0070f3; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
    </style>
</head>
<body>
    <h2>Select Your Financial Institution</h2>
    {% if previous_bank %}
    <h3>Previously used</h3>
    <form action="/set_bank/{{ ref }}" method="post">
        <input type="hidden" name="bank_url" value="{{ previous_bank['url'] }}">
        <button type="submit">{{ previous_bank['name'] }}</button>
    </form>
    <hr>
    {% endif %}
    <input type="text" id="search" placeholder="Search..." onkeyup="filterBanks()">
    <ul id="bankList">
        {% for bank in banks %}
        <li>
            <form action="/set_bank/{{ ref }}" method="post">
                <input type="hidden" name="bank_url" value="{{ bank.url }}">
                <button type="submit">{{ bank.name }}</button>
            </form>
        </li>
        {% endfor %}
    </ul>
<script>
function filterBanks() {
    let input = document.getElementById('search').value.toLowerCase();
    let items = document.querySelectorAll('#bankList li');
    items.forEach(li => {
        li.style.display = li.textContent.toLowerCase().includes(input) ? 'block' : 'none';
    });
}
</script>
</body>
</html>
""", banks=bank_list, ref=ref, previous_bank=previous_bank)

@app.route("/set_bank/<ref>", methods=["POST"])
def set_bank(ref):
    url = request.form.get("bank_url")
    resp = make_response(redirect(f"/mobile_redirect/{ref}?bank={url}"))
    resp.set_cookie("danielpay_bank", url, max_age=60*60*24*365)
    return resp

@app.route("/mobile_redirect/<ref>")
def mobile_redirect(ref):
    bank = request.args.get("bank")
    merchant = merchant_data.get(ref)
    if not bank or not merchant:
        return redirect("https://danielpay.ca/error")

    email = merchant["email"]
    amount = merchant["amount"]

    if bank == "td":
        return render_template_string(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting to TD</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <script>
    let isAndroid = /android/i.test(navigator.userAgent);
    if (isAndroid) {{
        window.location.href = 'intent://sendmoney?email={email}&amount={amount}#Intent;scheme=td;package=com.td;end';
    }} else {{
        window.location.href = 'https://easyweb.td.com';
    }}
    </script>
</head>
<body>
    <h2>Opening TD...</h2>
</body>
</html>
""")
    elif bank == "koho":
        return render_template_string(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting to KOHO</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <script>
    window.location.href = 'koho://etransfer/send?email={email}&amount={amount}';
    setTimeout(() => {{
        window.location.href = 'https://app.koho.ca';
    }}, 2500);
    </script>
</head>
<body>
    <h2>Opening KOHO...</h2>
</body>
</html>
""")
    else:
        return redirect(bank)

# Run with environment port for Render compatibility
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
