from dydx3 import Client
from decimal import Decimal

client = Client(
    host = 'https://api.dydx.exchange',
    api_key_credentials = {
        "walletAddress": "0x123",
        "secret": "123-aaaaa_bb-cc",
        "key": "1111111-aaaa-bbbb-cccc-11111111",
        "passphrase": "111111aaaafffffff",
        "legacySigning": False,
        "walletType": "METAMASK"},
    default_ethereum_address = '0x123',
    stark_private_key='111111aaaaaaa',
    network_id = 1)

# Get account balances
account_info = client.private.get_account().data['account']
market_info = client.public.get_markets().data['markets']
positions = account_info['openPositions']

def get_oracle_price(market):
    return Decimal(market_info[market]['oraclePrice'])

# ------- Liquidation price calculation -------
# S is the size of the position (positive if long, negative if short)
# P is the oracle price for the market
# I is the initial margin fraction for the market
# M is the maintenance margin fraction for the market

# Initial Margin Requirement = abs(S × P × I)
def get_imr(size, market):
    oracle_price = Decimal(market_info[market]['oraclePrice'])
    initial_margin_fraction = Decimal(market_info[market]['initialMarginFraction'])

    return abs(size * oracle_price * initial_margin_fraction)

# Maintenance Margin Requirement = abs(S × P × M)
def get_mmr(size, market):
    oracle_price = Decimal(market_info[market]['oraclePrice'])
    maintenance_margin_fraction = Decimal(market_info[market]['maintenanceMarginFraction'])

    return abs(size * oracle_price * maintenance_margin_fraction)

# Total Initial Margin Requirement = Σ abs(S_i × P_i × I_i)
def get_timr():
    total_initial_margin_requirement = Decimal(0)
    for position in positions.items():
        size = Decimal(position[1]['size'])
        market = position[1]['market']
        total_initial_margin_requirement += get_imr(size, market)

    return total_initial_margin_requirement

# Total Maintenance Margin Requirement = Σ abs(S_i × P_i × M_i)
def get_tmmr():
    total_initial_margin_requirement = Decimal(0)
    for position in positions.items():
        size = Decimal(position[1]['size'])
        market = position[1]['market']
        total_initial_margin_requirement += get_mmr(size, market)

    return total_initial_margin_requirement

# Q is the account's USDC balance (note that Q may be negative). In the API, this is called quoteBalance.
# Total Account Value = Q + Σ (S_i × P_i)
def get_tav():
    total_account_value = Decimal(0)
    quoteBalance = account_info['quoteBalance']
    for position in positions.items():
        size = Decimal(position[1]['size'])
        price = get_oracle_price(position[1]['market'])
        total_account_value += Decimal(quoteBalance) + size * price

    return total_account_value

# Function to calculate close price for a given position
def calculate_close_price(position):
    close_price = Decimal(0)

    market = position[1]['market']

    # P is the oracle price for the market
    price = get_oracle_price(position[1]['market'])

    # M is the maintenance margin fraction for the market
    maintenance_margin_fraction = Decimal(market_info[market]['maintenanceMarginFraction'])

    # V is the total account value, as defined above
    total_account_value = get_tav()

    # W is the total maintenance margin requirement, as defined above
    total_maintenance_margin_requirement = get_tmmr()

    size = Decimal(position[1]['size'])
    is_long = size > 0

    if is_long:
        # Close Price (Short) = P × (1 + (M × V / W))
        close_price = price * (1 - (maintenance_margin_fraction * total_account_value / total_maintenance_margin_requirement))
    else:
        # Close Price (Long) = P × (1 − (M × V / W))
        close_price = price * (1 + (maintenance_margin_fraction * total_account_value / total_maintenance_margin_requirement))

    docs_close_price = close_price
    # Liquidation price calculated as stated in the docs
    print('Variant 0: ' + str(round(float(docs_close_price), 4)))

    close_price = round(float(docs_close_price) * (1 + float(total_maintenance_margin_requirement) / float(price * size)), 4)
    print('Variant 1: ' + str(close_price))

    close_price = round(float(docs_close_price) * float(1 + maintenance_margin_fraction), 4)
    print('Variant 2: ' + str(close_price))

    close_price = round(float(docs_close_price) * 1.03, 4)
    print('Variant 3: ' + str(close_price))
    return close_price

def calculate_all_liq_prices():
    for position in positions.items():
        close_price = str(calculate_close_price(position))
        print(f"Close Price for position {position[1]['market']}: {close_price}")

calculate_all_liq_prices()

# Debug info
print('TMMR '+str(get_tmmr()))
print('QUOTE BALANCE = '+str(Decimal(account_info['quoteBalance'])))
print('TOTAL ACCOUNT VALUE = '+str(get_tav()))
print('EQUITY = '+account_info['equity'])
print('FREE COLLATERAL = '+account_info['freeCollateral'])
print('Account Info = '+str(account_info))