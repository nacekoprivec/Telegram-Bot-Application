import requests
from config import TELEGRAM_API_TOKEN

WEBHOOK_URL = "https://tgbdeploy-naces-projects.vercel.app/webhook"

url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/setWebhook"
params = {
    "url": WEBHOOK_URL
}
response = requests.get(url, params=params)

if response.status_code == 200:
    print("Webhook set successfully")
else:
    print(f"Failed to set webhook: {response.status_code}")
