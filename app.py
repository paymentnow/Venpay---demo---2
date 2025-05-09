
from flask import Flask, render_template_string, request, redirect, make_response

app = Flask(__name__)

merchant_data = {
    "abc123": {
        "merchant_name": "ABC Vending",
        "amount": "2.50",
        "email": "merchant@abc.ca"
    }
}

pay_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Venpay | Pay {{ merchant['merchant_name'] }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 40px; }
        .box { max-width: 400px; margin: auto; border: 1px solid #ccc; padding: 20px; border-radius: 10px; }
        button { font-size: 16px; padding: 10px 20px; background-color: #0070f3; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Pay {{ merchant['merchant_name'] }}</h2>
        <p>You're about to send <strong>${{ merchant['amount'] }}</strong> to <strong>{{ merchant['merchant_name'] }}</strong>.</p>
        <form action="/select_bank/{{ ref }}" method="get">
            <button type="submit">Yes, Send via My Bank</button>
        </form>
    </div>
</body>
</html>
"""

bank_select_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Select Your Bank | Venpay</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 40px; }
        .box { max-width: 400px; margin: auto; border: 1px solid #ccc; padding: 20px; border-radius: 10px; }
        button { font-size: 16px; margin: 10px; padding: 10px 20px; background-color: #0070f3; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Select Your Bank</h2>
        <p>This helps us open the correct app for e-Transfer next time.</p>
        <form action="/set_bank/{{ ref }}" method="post">
            <button name="bank" value="duca">DUCA</button>
            <button name="bank" value="td">TD</button>
            <button name="bank" value="other">Other</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/pay/<ref>")
def pay(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404

    bank = request.cookies.get("venpay_bank")
    if bank:
        return redirect(f"/bank_redirect/{ref}")

    return render_template_string(pay_template, merchant=merchant, ref=ref)

@app.route("/select_bank/<ref>", methods=["GET"])
def select_bank(ref):
    merchant = merchant_data.get(ref)
    return render_template_string(bank_select_template, merchant=merchant, ref=ref)

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

    if bank == "duca":
        return redirect("https://www.duca.com")
    elif bank == "td":
        return redirect("https://www.td.com")
    else:
        return redirect("https://www.google.com/search?q=how+to+send+e-transfer")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
