import json
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time  # Import the time module

# CoinMarketCap API Configuration
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
    'start': '1',
    'limit': '5000',
    'convert': 'USD'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '',  
}

# Email Configuration
sender_email = ""
receiver_email = ""
password = "" 

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_new_coins():
    try:
        response = requests.get(url, headers=headers, params=parameters)
        data = json.loads(response.text)
        new_coins = []
        now = datetime.utcnow()
        print(f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        for coin in data.get('data', []):
            try:
                date_added_str = coin.get('date_added')
                if date_added_str:
                    date_added = datetime.strptime(date_added_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    if (now - date_added).total_seconds() <= 2400:  # 2400 seconds = 40 minutes
                        name = coin['name']
                        symbol = coin['symbol']
                        platform = coin.get('platform', {})
                        fully_diluted_market_cap = coin['quote']['USD'].get('fully_diluted_market_cap', 0)
                        price = coin['quote']['USD'].get('price', 0)
                        release_time = date_added.strftime('%Y-%m-%d %H:%M:%S UTC')
                        platform_name = platform.get('name', 'Unknown Platform')
                        token_address = platform.get('token_address', 'No address available')
                        
                        new_coins.append(
                            f"Name: {name}\nSymbol: {symbol}\nPlatform: {platform_name}\nToken Address: {token_address}\n"
                            f"Price: USD {price}\nFully Diluted Market Cap: USD {fully_diluted_market_cap}\nRelease Time: {release_time}\n"
                        )
            except Exception as e:
                print(f"Error processing coin data: {e}")

        if new_coins:
            email_body = "New coins released in the last 40 minutes:\n\n" + "\n".join(new_coins)
            send_email("New CoinMarketCap Listings", email_body)
        else:
            print("No new coins added in the last 40 minutes.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        send_email("CoinMarketCap API Error", f"Failed to fetch data: {e}")


# Run the check every minute
while True:
    check_new_coins()
    time.sleep(40)
