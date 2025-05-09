
from flask import Flask, render_template_string, request, redirect, make_response

app = Flask(__name__)

merchant_data = {
    "abc123": {
        "merchant_name": "DanielPay Vending",
        "amount": "0.01",
        "email": "d.saindon09@gmail.com"
    }
}

bank_list = [
    {"name": "DUCA", "url": "https://www.duca.com"},
    {"name": "TD", "url": "https://easyweb.td.com"},
    {"name": "RBC", "url": "https://www.rbcroyalbank.com/personal.html"},
    {"name": "CIBC", "url": "https://www.cibc.com"},
    {"name": "Scotiabank", "url": "https://www.scotiabank.com"},
    {"name": "BMO", "url": "https://www.bmo.com"},
    {"name": "National Bank", "url": "https://www.nbc.ca"},
    {"name": "Desjardins", "url": "https://www.desjardins.com"},
    {"name": "Meridian", "url": "https://www.meridiancu.ca"},
    {"name": "Vancity", "url": "https://www.vancity.com"},
    {"name": "Coast Capital", "url": "https://www.coastcapitalsavings.com"},
    {"name": "Alterna", "url": "https://www.alterna.ca"},
    {"name": "Tangerine", "url": "https://www.tangerine.ca"}
]

# Templates as strings
pay_template = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>DanielPay | Pay {{ merchant['merchant_name'] }}</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 40px; }
        .box { max-width: 400px; margin: auto; border: 1px solid #ccc; padding: 20px; border-radius: 10px; }
        button { font-size: 16px; padding: 10px 20px; background-color: #0070f3; color: white; border: none; border-radius: 5px; cursor: pointer; }
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
"""

bank_search_template = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Select Bank | DanielPay</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
        input { width: 90%; padding: 10px; font-size: 16px; }
        ul { list-style: none; padding: 0; max-height: 300px; overflow-y: auto; }
        li { margin: 8px 0; }
        button { font-size: 16px; padding: 8px 14px; background-color: #0070f3; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
    </style>
</head>
<body>
    <h2>Select Your Bank or Credit Union</h2>
    <p>Start typing and choose your institution</p>
    <input type="text" id="search" placeholder="Start typing..." onkeyup="filterBanks()">
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
"""

@app.route("/pay/<ref>")
def pay(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404

    bank_url = request.cookies.get("danielpay_bank")
    if bank_url:
        return redirect(f"/bank_redirect/{ref}")

    return render_template_string(pay_template, merchant=merchant, ref=ref)

@app.route("/select_bank/<ref>")
def select_bank(ref):
    return render_template_string(bank_search_template, banks=bank_list, ref=ref)

@app.route("/set_bank/<ref>", methods=["POST"])
def set_bank(ref):
    url = request.form.get("bank_url")
    resp = make_response(redirect(f"/bank_redirect/{ref}"))
    resp.set_cookie("danielpay_bank", url, max_age=60*60*24*365)
    return resp

@app.route("/bank_redirect/<ref>")
def bank_redirect(ref):
    url = request.cookies.get("danielpay_bank")
    return redirect(url or "https://www.google.com/search?q=how+to+send+e-transfer")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
