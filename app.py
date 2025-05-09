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
</head>
<body>
    <div style='text-align: center; margin-top: 50px;'>
        <h2>Make Your Purchase</h2>
        <p>You're about to send ${{ merchant['amount'] }}.</p>
        <form action='/select_bank/{{ ref }}' method='get'>
            <button type='submit' style='padding: 10px 20px; font-size: 16px;'>Yes, Send via My Bank</button>
        </form>
    </div>
</body>
</html>
""", merchant=merchant, ref=ref)

@app.route("/select_bank/<ref>")
def select_bank(ref):
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Select Your Bank</title>
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
</head>
<body>
    <div style='text-align: center; margin-top: 50px;'>
        <h2>Select Your Financial Institution</h2>
        <form action='/set_bank/{{ ref }}' method='post'>
            <input type='text' id='search' onkeyup='filterBanks()' placeholder='Search...' style='width: 200px; padding: 10px;'>
            <ul id='bankList' style='list-style-type: none; padding: 0; display: none;'>
                <li><button name='bank' value='td' type='submit' style='margin: 10px;'>TD</button></li>
                <li><button name='bank' value='koho' type='submit' style='margin: 10px;'>KOHO</button></li>
                <li><button name='bank' value='duca' type='submit' style='margin: 10px;'>DUCA</button></li>
            </ul>
        </form>
    </div>
</body>
</html>
""", ref=ref)

@app.route("/set_bank/<ref>", methods=["POST"])
def set_bank(ref):
    bank = request.form.get("bank")
    resp = make_response(redirect(f"/bank_redirect/{ref}"))
    resp.set_cookie("danielpay_bank", bank, max_age=60*60*24*365)
    return resp

@app.route("/bank_redirect/<ref>")
def bank_redirect(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404

    bank = request.cookies.get("danielpay_bank")
    email = merchant["email"]
    amount = merchant["amount"]

    if bank == "koho":
        return redirect(f"koho://etransfer/send?email={email}&amount={amount}")
    elif bank == "td":
        return redirect(f"intent://sendmoney?email={email}&amount={amount}#Intent;scheme=td;package=com.td;end")
    elif bank == "duca":
        return redirect("https://www.duca.com")
    else:
        return redirect("https://www.google.com/search?q=how+to+send+e-transfer")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
