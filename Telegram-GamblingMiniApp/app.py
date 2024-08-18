import os
from flask import Flask, request, jsonify, render_template
import stripe
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  

stripe.api_key = os.getenv("STRIPE_API_KEY")



FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '5c349d4aa213fe5703ec3ec125db77e6e2dfe89db9de8539')

app.config['SECRET_KEY'] = FLASK_SECRET_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        amount = request.json.get('amount')

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Deposit',
                    },
                    'unit_amount': amount * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://gamblingminiapp.vercel.app/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://gamblingminiapp.vercel.app/cancel',
        )
        return jsonify(id=session.id)
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/success')
def success():
    session_id = request.args.get('session_id')
    return f"Payment succeeded! Session ID: {session_id}"

@app.route('/cancel')
def cancel():
    return "Payment canceled!"



if __name__ == '__main__':
    app.run(port=5000, debug=True)
