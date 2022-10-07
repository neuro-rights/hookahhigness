# import the OpenseaAPI object from the opensea module
from opensea import OpenseaAPI
# fetch multiple events
from opensea import utils as opensea_utils

# Import the login_required decorator
from django.contrib.auth.decorators import login_required


def test():
    """ """

    # API_KEY - Etherscan api key, you get one after registration
    OPENSEA_CONTRACT = '0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b'
    url = '<https://api.etherscan.io/api>'
    params = {
      'module': 'logs',
      'action': 'getLogs',
      'fromBlock' : BLOCK_START,
      'toBlock': 'latest',
      'address': OPENSEA_CONTRACT,
      'apikey': API_KEY
    }
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)["result"]


    url = '<https://api.etherscan.io/api>'
    params = {
      'module': 'block',
      'action': 'getblocknobytime',
      'timestamp' : int(time.time() // 1),
      'closest': 'before',
      'apikey': API_KEY
    }
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)["result"]
    LATEST_BLOCK = int(json_data)
    BLOCK_START = LATEST_BLOCK - 40

    data = "0x00000000000000000000000000000000000000000000000000000000000000007656e0665c6bdc38947d580d2e8c4c19ba8fa4019abb8fef31cfaa1b7645f00d000000000000000000000000000000000000000000000000027f7d0bdb920000"
    price_wei = int("0x" + data[-64:], 16)
    price_eth = price_wei / 10**18

    # obtaning latest transactions
    transactions = get_latest_transactions()

    # signature of OrdersMatched method
    OrdersMatchedSig = "0xc4109843e0b7d514e4c093114b863f8e7d8d9a458c372cd51bfe526b588006c9"

    # to convert wei to ETH
    DIVIDER = 10**18

    # storing refactored transactions 
    transactions_refactored = []
    for tr in transactions:
        result = {}
        if tr['topics'][0] == OrdersMatchedSig:
            result['maker'] = '0x' + (sample['topics'][1])[26:]
            result['taker'] = '0x' + (sample['topics'][2])[26:]
            result['price'] = int('0x' + sample['data'][-32:], 16) / DIVIDER
            #....  We could also add to 'result' other details from 'tr'
            #....  such as timeStamp, blockNumber, etc.                    
            transactions_refactored.append(result)


def get_transaction_receipt(txn):
    url = '<https://api.etherscan.io/api>'
    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionReceipt',
        'apikey': API_KEY,
        'txhash' : txn
    }
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)["result"]
    return json_data


WETH_CONTRACT = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
OPENSEA_CONTRACT = '0x7be8076f4ea4a4ad08075c2508e481d6c946d12b'
TRANSFER_METHOD = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

# txn - transaction hash
def determine_currency(txn):
    # mentioned earlier function
    transaction_receipt = get_transaction_receipt(txn) 
    currency = 'ETH'

    # OrdersMatched will always be the last element in receipt array
    price_hex = transaction_receipt['logs'][-1]['data'][-64:]
    for s in transaction_receipt['logs']:
        if s['topics'][0] == TRANSFER_METHOD:
              # check if price in Transfer event parameters
            if price_hex in s['data']:
                  # additional check if currenct is Wrapped ETH
                if s['address'] == WETH_CONTRACT:
                    currency = 'WETH'
                else:
                    currency = 'NONETH-' +s['address']

    return currency


# txn - transaction hash
def determine_collection_contract(txn):
    # mentioned earlier function
    transaction_receipt = get_transaction_receipt(txn) 
  
    # OrdersMatched will always be the last element in receipt array
    price_hex = transaction_receipt['logs'][-1]['data'][-64:]
    collection_contract = ''
    token_number = -1
    for s in transaction_receipt['logs']:
        if (s['topics'][0] == TRANSFER_METHOD):
          # eliminating ERC-20 contracts
            if price_hex not in s['data']:
                collection_contract = s['address']
                token_number = int(s['topics'][3], 16)
        
    return collection_contract, token_number


def get_collection_name(contract_adress):
    url = 'https://blockscout.com/eth/mainnet/api'
    params = {
        'module' : 'token',
        'action' : 'getToken',
        'contractaddress' : contract_adress
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        json_data = json.loads(r.text)
        if (json_data != None) and (json_data['message'] == 'OK'):
            return json_data['result']['symbol']
        else:
            return "None"
    else:
        return "None"

##############################################
def get_events(start_date, end_date, cursor='', event_type='successful', **kwargs):
    url = "https://api.opensea.io/api/v1/events"
    query = { 
        "only_opensea": "false", 
        "occurred_before": end_date,
        "occurred_after": start_date,
        "event_type": event_type,
        "cursor": cursor,
         **kwargs
    }

    headers = {
        "Accept": "application/json",
        "X-API-KEY": OPENSEA_APIKEY
    }
    response = requests.request("GET", url, headers=headers, params=query)

    return response.json()


def parse_event(event):
    record = {}
    asset = event.get('asset')
    if asset == None:
        return None # if there's no asset that means it's not a single NFT transaction so skip this item

    #collection
    record['collection_slug'] = asset['collection']['slug']
    record['collection_name'] = asset['collection']['name']
    record['collection_url'] = "https://opensea.io/collection/" + asset['collection']['slug']

    #asset
    record['asset_id'] = asset['id']
    record['asset_name'] = asset['name']
    record['asset_description'] = asset['description']
    record['asset_contract_date'] = asset['asset_contract']['created_date']
    record['asset_url'] = asset['permalink']
    record['asset_img_url'] = asset['image_url']

    #event
    record['event_id'] = event['id']
    record['event_time'] = event.get('created_date')
    record['event_auction_type'] = event.get('auction_type')
    record['event_contract_address'] = event.get('contract_address')
    record['event_quantity'] = event.get('quantity')
    record['event_payment_symbol'] =  None if event.get('payment_token') == None else event.get('payment_token').get('symbol')

    decimals = 18
    if event.get('payment_token') != None:
        decimals = event.get('payment_token').get('decimals')

    price_str = event['total_price']

    try: 
        if len(price_str) < decimals:
            price_str =  "0." + (decimals-len(price_str)) * "0" + price_str
            record['event_total_price'] = float(price_str)
        else:
            record['event_total_price'] = float(price_str[:-decimals] + "." + price_str[len(price_str)-decimals:])
    except:
        print(event)

    return record

def fetch_all_events(start_date, end_date, pause=1, **kwargs):
    result = list()
    next = ''
    fetch = True

    print(f"Fetching events between {start_date} and {end_date}")
    while fetch:
        response = get_events(int(start_date.timestamp()), int(end_date.timestamp()), cursor=next, **kwargs)

        for event in response['asset_events']:
            cleaned_event = parse_event(event)
            
            if cleaned_event != None:
                result.append(cleaned_event)

        if response['next'] is None:
            fetch = False
        else:
            next = response['next']

        sleep(pause)

    return result


def write_csv(data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = data[0].keys())

        writer.writeheader()
        for event in data:
            writer.writerow(event)   


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


def valid_datetime(arg_datetime_str):
    try:
        return datetime.strptime(arg_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(arg_datetime_str, "%Y-%m-%d")
        except ValueError:
            msg = "Given Datetime ({0}) not valid! Expected format, 'YYYY-MM-DD' or 'YYYY-MM-DD HH:mm'!".format(arg_datetime_str)
            raise argparse.ArgumentTypeError(msg)  


#res = fetch_all_events(args.startdate.replace(tzinfo=timezone.utc), args.enddate.replace(tzinfo=timezone.utc), args.pause)


@login_required
def opensea(request):
    # create an object to interact with the Opensea API (need an api key)
    api = OpenseaAPI(apikey="YOUR APIKEY")
    # fetch a single asset
    contract_address = "0x495f947276749Ce646f68AC8c248420045cb7b5e"
    token_id = "66406747123743156841746366950152533278033835913591691491127082341586364792833"
    result = api.asset(asset_contract_address=contract_address, token_id=token_id)
    # fetch multiple assets
    result = api.assets(owner="0xce90a7949bb78892f159f428d0dc23a8e3584d75", limit=3)
    # fetch a single contract
    result = api.contract(asset_contract_address="0x495f947276749Ce646f68AC8c248420045cb7b5e")
    # fetch a single collection
    result = api.collection(collection_slug="cryptopunks")
    # fetch multiple collections
    result = api.collections(asset_owner="0xce90a7949bb78892f159f428d0dc23a8e3584d75", limit=3)
    # fetch collection stats
    result = api.collection_stats(collection_slug="cryptopunks")

    period_end = opensea_utils.datetime_utc(2021, 11, 6, 14, 30)
    result = api.events(
        occurred_before=period_end,
        limit=10,
        export_file_name="events.json",
    )

    # fetch multiple bundles
    result = api.bundles(limit=2)
    # paginate the events endpoint (cursors are handled internally)
    from datetime import datetime, timezone
    #
    start_at = datetime(2021, 10, 5, 3, 25, tzinfo=timezone.utc)
    finish_at = datetime(2021, 10, 5, 3, 20, tzinfo=timezone.utc)
    #
    event_generator = api.events_backfill(start=start_at,
                                          until=finish_at,
                                          event_type="successful")
    for event in event_generator:
        if event is not None:
            print(event) # or do other things with the event data
        pass
