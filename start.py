import os
from tools.Transactions import Transactions
from dotenv import load_dotenv

load_dotenv()

ABI_PATH = os.getenv('ABI_PATH')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
DAYS_AGO = 120

if __name__ == '__main__':
    client = Transactions(abi_path=ABI_PATH, contract_address=CONTRACT_ADDRESS, server_address=SERVER_ADDRESS)
    client.get_transaction_data(days_ago=DAYS_AGO)