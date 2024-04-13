import requests
from datetime import datetime, timedelta, timezone
import tzlocal
from pymongo import MongoClient
import json

def saveDataToDB(data):
    try:
        print(data)
        client = MongoClient('mongodb://localhost:27017/')
        db = client['INF7225']
        collection = db['historicalPrices']
        inserted_data = collection.insert_one(data)
        return inserted_data.inserted_id
        # print("data inserted successfully. IÃ inserted ID:", inserted_data.inserted_id)
    except Exception as e:
        print(f"error saving data to DB: {e}")


def getHistoricalPrices(coin, period_unit, period_count):

    if period_unit.lower() == "hours":
        interval = "hour"
    elif period_unit.lower() == "days":
        interval = "day"
    else:
        print("invalid period unit. please specify 'hours' or 'days'.")
        return None

    local_zone = tzlocal.get_localzone()
    endTime = datetime.now(local_zone)
    startTime = endTime - timedelta(hours=period_count) if period_unit.lower() == "hours" else endTime - timedelta(days=period_count)
    endTimeStamp = int(endTime.timestamp())
    startTimeStamp = int(startTime.timestamp())

    # url of cyptocompare api for fetching data
    url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}?fsym={coin}&tsym=USD&limit={period_count}&toTs={endTimeStamp}&aggregate=1"

    try:
        response = requests.get(url)
        data = response.json()
        if 'Data' in data and 'Data' in data['Data']:
            price_data = data['Data']['Data']
            if len(price_data) >= period_count:
                for i in price_data:
                    i['time'] = datetime.fromtimestamp(i['time'], local_zone).strftime('%Y-%m-%d %H:%M:%S')
                
                returned_data = {'insertion_datetime': datetime.now(local_zone).strftime('%Y-%m-%d %H:%M:%S'),'coin' : coin , 'period_count' : period_count , 'period_unit' : period_unit ,  'prices_data': price_data}
                data_inserted_id = saveDataToDB(returned_data)
                return data_inserted_id
            else:
                print("error: Insufficient data points was collected.")
                return None
        else:
            print("error: Unexpected response format.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"error fetching data: {e}")
        return None


# Example usage
# btc_prices = getHistoricalPrices("BTC", "hours",20)
#if btc_prices:

    #print("BTC Prices:",  btc_prices )


# eth_prices = getHistoricalPrices("ETH", "days",2)
# #if eth_prices :
#     #print("ETH Prices:", eth_prices)