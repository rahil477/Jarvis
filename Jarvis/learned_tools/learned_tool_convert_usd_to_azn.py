def learned_tool_convert_usd_to_azn():
    import requests
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    response = requests.get(url)
    data = response.json()
    usd_rate = data['rates']['AZN']
    return f'$1 {usd_rate} AZN.'