
from flask import Flask, render_template_string, request, redirect, make_response

app = Flask(__name__)

merchant_data = {
    "abc123": {
        "merchant_name": "DanielPay Vending",
        "amount": "0.01",
        "email": "d.saindon09@gmail.com"
    }
}

@app.route("/pay/<ref>")
def pay(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Make Your Purchase</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 40px; font-size: 18px; }
        button { padding: 12px 24px; font-size: 18px; background-color: #0070f3; color: white; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
    </style>
</head>
<body>
    <h2>Make Your Purchase</h2>
    <p>You're about to send <strong>${{ merchant['amount'] }}</strong>.</p>
    <form action='/select_bank/{{ ref }}' method='get'>
        <button type='submit'>Yes, Send via My Bank</button>
    </form>
</body>
</html>
""", merchant=merchant, ref=ref)

@app.route("/select_bank/<ref>")
def select_bank(ref):
    previous = request.cookies.get("venpay_bank")
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Select Your Financial Institution</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; font-size: 18px; }
        input { width: 90%; padding: 10px; font-size: 18px; margin: 10px auto; }
        ul { list-style-type: none; padding: 0; margin-top: 10px; display: none; }
        li { margin: 10px 0; }
        button { font-size: 18px; padding: 10px 20px; background-color: #0070f3; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
        .saved { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h2>Select Your Financial Institution</h2>
    <form action="/set_bank/{{ ref }}" method="post">
        {% if previous %}
        <div class="saved">
            <button type="submit" name="bank" value="{{ previous }}">{{ previous }}</button>
        </div>
        {% endif %}
        <input type="text" id="search" placeholder="Search..." onkeyup="filterBanks()">
        <ul id="bankList">
            <li><button name="bank" value="TD" type="submit">TD</button></li>
            <li><button name="bank" value="KOHO" type="submit">KOHO</button></li>
            <li><button name="bank" value="DUCA" type="submit">DUCA</button></li>
        </ul>
    </form>
    <script>
        function filterBanks() {
            let input = document.getElementById('search').value.toLowerCase();
            let list = document.getElementById('bankList');
            let items = list.querySelectorAll('li');
            let anyVisible = false;
            items.forEach(li => {
                const match = li.textContent.toLowerCase().includes(input);
                li.style.display = match ? 'block' : 'none';
                if (match) anyVisible = true;
            });
            list.style.display = anyVisible ? 'block' : 'none';
        }
    </script>
</body>
</html>
""", ref=ref, previous=previous)

@app.route("/set_bank/<ref>", methods=["POST"])
def set_bank(ref):
    bank = request.form.get("bank")
    resp = make_response(redirect(f"/bank_redirect/{ref}?bank={bank}"))
    resp.set_cookie("venpay_bank", bank, max_age=60*60*24*365)
    return resp

@app.route("/bank_redirect/<ref>")
def bank_redirect(ref):
    merchant = merchant_data.get(ref)
    bank = request.args.get("bank")
    if not merchant or not bank:
        return "Merchant or bank info missing", 404

    email = merchant["email"]
    amount = merchant["amount"]
    if bank == "KOHO":
        return redirect(f"koho://etransfer/send?email={email}&amount={amount}")
    elif bank == "TD":
        user_agent = request.headers.get("User-Agent", "").lower()
        if "android" in user_agent:
            return redirect(f"intent://sendmoney?email={email}&amount={amount}#Intent;scheme=td;package=com.td;end")
        else:
            return redirect("https://easyweb.td.com")
    elif bank == "DUCA":
        return redirect("https://www.duca.com/OnlineBanking")
    else:
        return redirect("https://www.google.com/search?q=how+to+send+e-transfer")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
