from flask import Flask, request, jsonify
import requests
from config import TELEGRAM_API_TOKEN, parametersGet, url_telegram
import random

app = Flask(__name__)

class Player:
    def __init__(self, data):
        first_name = data["message"]["from"].get("first_name", "")
        last_name = data["message"]["from"].get("last_name", "")
        self.full_name = f"{first_name} {last_name}"
        self.balance = random.randint(1, 10000)

    def decreaseBalance(self, amount):
        self.balance -= amount

players = {}

def get_updates(offset=None):
    params = parametersGet.copy()
    if offset:
        params['offset'] = offset
    response = requests.get(f'{url_telegram}/getUpdates', params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching updates: {response.status_code}")
        return {}

def send_message(chat_id, text):
    params = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(f'{url_telegram}/sendMessage', params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error sending message: {response.status_code}")
        return {}

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json

    if update.get('message'):
        chat_id = update['message']['chat']['id']
        player_id = update['message']['from'].get("id", "")
        message_text = update['message'].get('text', '')

        response_text = ""

        if message_text.startswith('/'):
            command = message_text.lower()

            if command == '/start':
                if player_id not in players:
                    player = Player(update)
                    players[player_id] = player
                response_text = f'Welcome {players[player_id].full_name}! Use /balance to check your balance and /bet to place a bet.'

            elif command == '/balance':
                if player_id in players:
                    player = players[player_id]
                    response_text = f"Your balance is {player.balance:}€."
                else:
                    response_text = f"Type /start in order to make an account."
                
            elif command == '/bet':
                if player_id in players:
                    response_text = f"Place your bet using /bet <amount>."
                else:
                    response_text = f"There is no account {update['message']['from'].get('first_name', '')} {update['message']['from'].get('last_name', '')}. Type /start to make one."
                
            elif message_text.startswith('/bet '):
                if player_id in players:
                    try:
                        amount = int(message_text.split(' ')[1])
                        if amount <= 0:
                            response_text = "Bet amount must be a positive integer."
                        elif amount > players[player_id].balance:
                            response_text = "Insufficient balance."
                        else:
                            players[player_id].decreaseBalance(amount)
                            response_text = f"You have successfully bet {amount}€. Your new balance is {players[player_id].balance}€."
                    except (IndexError, ValueError):
                        response_text = "Please provide a valid integer amount for the bet."
                else:
                    response_text = f"There is no account {update['message']['from'].get('first_name', '')} {update['message']['from'].get('last_name', '')}. Type /start to make one."

            else:
                response_text = "Unknown command. Use /start for help."

            send_message(chat_id, response_text)

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
