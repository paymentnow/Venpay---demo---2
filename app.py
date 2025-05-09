from flask import Flask, render_template_string, request, redirect, make_response

app = Flask(__name__)

merchant_data = {
    "abc123": {
        "merchant_name": "DanielPay Vending",
        "amount": "0.01",
        "email": "d.saindon09@gmail.com"
    }
}

pay_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Make Your Purchase</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 100px; }
        .button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-size: 16px; }
    </style>
</head>
<body>
    <h2>Make Your Purchase</h2>
    <p>You're about to send ${{ merchant.amount }}.</p>
    <form method="GET" action="/select_bank/{{ ref }}">
        <button type="submit" class="button">Yes, Send via My Bank</button>
    </form>
</body>
</html>
"""

bank_select_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Select Your Financial Institution</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 60px; }
        .bank-button { display: block; margin: 10px auto; width: 180px; padding: 10px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 6px; }
        #bankList { display: none; }
    </style>
</head>
<body>
    <h2>Select Your Financial Institution</h2>
    <form method="POST" action="/set_bank/{{ ref }}">
        <input type="text" id="search" placeholder="Search..." onkeyup="filterBanks()" style="width: 80%; padding: 8px; font-size: 16px;"><br>
        {% if bank %}
        <button type="submit" name="bank" value="{{ bank }}" class="bank-button">Use {{ bank }}</button>
        {% endif %}
        <div id="bankList">
            <button type="submit" name="bank" value="TD" class="bank-button">TD</button>
            <button type="submit" name="bank" value="KOHO" class="bank-button">KOHO</button>
            <button type="submit" name="bank" value="DUCA" class="bank-button">DUCA</button>
        </div>
    </form>
    <script>
        const bankList = document.getElementById("bankList");
        const search = document.getElementById("search");

        function filterBanks() {
            const val = search.value.toUpperCase();
            const buttons = bankList.querySelectorAll("button");
            let show = false;
            buttons.forEach(btn => {
                if (btn.textContent.toUpperCase().includes(val)) {
                    btn.style.display = "block";
                    show = true;
                } else {
                    btn.style.display = "none";
                }
            });
            bankList.style.display = show ? "block" : "none";
        }
    </script>
</body>
</html>
"""

redirect_template = """
<!DOCTYPE html>
<html>
<head><title>Opening App</title></head>
<body>
    <h2>Opening your banking app...</h2>
    <p>If it doesn't open automatically, tap below:</p>
    <a href="{{ link }}">Open App</a>
    <script>window.location.href="{{ link }}";</script>
</body>
</html>
"""

@app.route("/pay/<ref>")
def pay(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404
    return render_template_string(pay_template, merchant=merchant, ref=ref)

@app.route("/select_bank/<ref>", methods=["GET"])
def select_bank(ref):
    merchant = merchant_data.get(ref)
    bank = request.cookies.get("venpay_bank")
    return render_template_string(bank_select_template, merchant=merchant, ref=ref, bank=bank)

@app.route("/set_bank/<ref>", methods=["POST"])
def set_bank(ref):
    bank = request.form.get("bank")
    resp = make_response(redirect(f"/bank_redirect/{ref}"))
    resp.set_cookie("venpay_bank", bank, max_age=60*60*24*365)
    return resp

@app.route("/bank_redirect/<ref>")
def bank_redirect(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404
    bank = request.cookies.get("venpay_bank")
    email = merchant["email"]
    amount = merchant["amount"]

    if bank == "KOHO":
        return render_template_string(redirect_template, link=f"koho://etransfer/send?email={email}&amount={amount}")
    elif bank == "TD":
        return render_template_string(redirect_template, link=f"intent://sendmoney?email={email}&amount={amount}#Intent;scheme=td;package=com.td;end")
    elif bank == "DUCA":
        return render_template_string(redirect_template, link="https://www.duca.com/OnlineBanking")
    else:
        return redirect("https://www.google.com/search?q=how+to+send+e-transfer")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)