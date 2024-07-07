import aiohttp
import asyncio
import json
import sys
from datetime import datetime, timedelta

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

class PrivatBankAPIClient:
    def __init__(self, days):
        self.days = days

    async def fetch_rate_for_date(self, session, date):
        async with session.get(f"{API_URL}{date}") as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

    async def fetch_exchange_rates(self):
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.days):
                date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(self.fetch_rate_for_date(session, date))

            rates = await asyncio.gather(*tasks)
            for rate in rates:
                if rate:
                    date = rate['date']
                    for exchange_rate in rate['exchangeRate']:
                        if exchange_rate['currency'] in ['USD', 'EUR']:
                            result = {
                                date: {
                                    exchange_rate['currency']: {
                                        'sale': exchange_rate.get('saleRate', exchange_rate.get('saleRateNB')),
                                        'purchase': exchange_rate.get('purchaseRate', exchange_rate.get('purchaseRateNB'))
                                    }
                                }
                            }
                            results.append(result)
        return results

async def main(days):
    client = PrivatBankAPIClient(days)
    rates = await client.fetch_exchange_rates()
    print(json.dumps(rates, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_days>")
        sys.exit(1)

    days = int(sys.argv[1])
    if days > 10:
        print("The maximum number of days is 10.")
        sys.exit(1)

    asyncio.run(main(days))
