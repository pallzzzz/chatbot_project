from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def index():
    # User se input le rahe hain jo Dialogflow se aayega
    data = request.get_json()

    # Print the received data for debugging
    print("Received Data:", data)  # Debugging line

    try:
        # Source currency, amount, aur target currency ko fetch karna
        if 'queryResult' in data and 'parameters' in data['queryResult']:
            source_currency = data['queryResult']['parameters'].get('unit-currency', {}).get('currency', '')
            amount = float(data['queryResult']['parameters'].get('unit-currency', {}).get('amount', 0))
            target_currency = data['queryResult']['parameters'].get('currency-name', '')

            # Check if target_currency is a list, and if so, access the first item
            if isinstance(target_currency, list):
                target_currency = target_currency[0]

            print(f"Source Currency: {source_currency}")
            print(f"Amount: {amount}")
            print(f"Target Currency: {target_currency}")

            # Currency conversion ko call karte hain
            converted_amount = convert_currency(source_currency, target_currency, amount)

            if converted_amount:
                response_text = f"{amount} {source_currency} is equal to {converted_amount} {target_currency}."
            else:
                response_text = "Sorry, conversion rate is not available for the requested currencies."
        else:
            response_text = "Invalid data format received."

    except Exception as e:
        response_text = f"Error processing request: {str(e)}"

    return {"fulfillmentText": response_text}

def convert_currency(source, target, amount):
    # Conversion factor fetch karna
    conversion_rate = fetch_conversion_factor(source, target)

    if conversion_rate:
        # Converted amount calculate karna
        converted_amount = round(amount * conversion_rate, 2)
        return converted_amount
    else:
        return None

def fetch_conversion_factor(source, target):
    api_key = "ab37cab2129b265dd8f75891"  # API key yahan set karein
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{source}"

    try:
        response = requests.get(url)
        data = response.json()

        if data['result'] == 'success' and target in data['conversion_rates']:
            conversion_rate = data['conversion_rates'][target]
            print(f"1 {source} = {conversion_rate} {target}")
            return conversion_rate
        else:
            print(f"Conversion rate for {target} is not available.")
            return None
    except Exception as e:
        print(f"API request failed: {str(e)}")
        return None

if __name__ == "__main__":
    app.run(debug=True)

