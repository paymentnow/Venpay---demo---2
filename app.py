
from flask import Flask, render_template, request, redirect, make_response

app = Flask(__name__)

merchant_data = {
    "abc123": {
        "merchant_name": "ABC Vending",
        "amount": "2.50",
        "email": "merchant@abc.ca"
    }
}

@app.route("/pay/<ref>")
def pay(ref):
    merchant = merchant_data.get(ref)
    if not merchant:
        return "Merchant not found", 404

    bank = request.cookies.get("venpay_bank")
    if bank:
        return redirect(f"/bank_redirect/{ref}")

    return render_template("pay.html", merchant=merchant, ref=ref)

@app.route("/select_bank/<ref>", methods=["GET"])
def select_bank(ref):
    merchant = merchant_data.get(ref)
    return render_template("bank_select.html", merchant=merchant, ref=ref)

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

    if bank == "koho":
        return redirect(f"koho://etransfer/send?email={email}&amount={amount}")
    elif bank == "tangerine":
        return redirect(f"intent://sendmoney?email={email}&amount={amount}#Intent;scheme=tangerine;package=com.tangerine;end")
    else:
        return redirect("https://www.google.com/search?q=how+to+send+e-transfer")

if __name__ == "__main__":
    app.run(debug=True)
