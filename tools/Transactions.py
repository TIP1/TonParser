import os
import json
import time
import datetime

from tonclient.client import TonClient
from tonclient.types import Abi, ParamsOfQueryCollection, ParamsOfRunTvm, ParamsOfEncodeMessage, CallSet, Signer, ParamsOfSendMessage, ParamsOfDecodeMessage, ParamsOfParse, NetworkConfig, CryptoConfig, AbiConfig, BocConfig, ProofsConfig, ClientConfig


class Transactions:

    def __init__(self, abi_path, contract_address, server_address):
        self.abi_path = abi_path
        self.contract_address = contract_address
        self.server_address = server_address

        with open(abi_path, 'r') as abi_file:
            self.contract_abi = json.load(abi_file)

        # CONFIGS
        # Network config with your endpoint and API key
        self.network = NetworkConfig(
            server_address=server_address
        )

        # Default crypto config
        self.crypto = CryptoConfig()

        # Default abi config
        self.abi = AbiConfig()

        # Default boc config
        self.boc = BocConfig()

        # Default proofs config
        self.proofs = ProofsConfig()

        # Create the ClientConfig object
        self.config = ClientConfig(network=self.network, crypto=self.crypto, abi=self.abi, boc=self.boc, proofs=self.proofs)

        self.client = TonClient(config=self.config)

    # METHODS
    def call_get_rate(self, from_timestamp, to_timestamp):
        # Set the call parameters
        call_set = CallSet(
            function_name='getRate',
            input={'answerId': 1, '_fromTimestamp': from_timestamp, '_toTimestamp': to_timestamp}
        )

        query_result = self.client.net.query_collection(
            ParamsOfQueryCollection(
                collection='accounts',
                filter={'id': {'eq': self.contract_address}},
                result='boc'
            )
        )

        if not query_result.result:
            raise Exception('Account not found or BOC data not available')

        account_boc = query_result.result[0]['boc']

        # Prepare the message encoding parameters
        encode_params = ParamsOfEncodeMessage(
            abi=Abi.Json(value=json.dumps(self.contract_abi)),
            address=self.contract_address,
            call_set=call_set,
            signer=Signer.NoSigner()
        )

        # Encode the message
        encoded = self.client.abi.encode_message(params=encode_params)

        # Send the message
        send_params = ParamsOfSendMessage(
            message=encoded.message,
            send_events=False
        )
        wait_params = ParamsOfRunTvm(
            message=encoded.message,
            account=account_boc
        )
        result = self.client.tvm.run_tvm(params=wait_params)
        decode_body_params = ParamsOfDecodeMessage(
            abi=Abi.Json(value=json.dumps(self.contract_abi)),
            message=result.out_messages[0]
        )
        decoded_body = self.client.abi.decode_message(params=decode_body_params)
        # value0 = decoded_body.value['value0']
        # value1 = decoded_body.value['value1']

        return decoded_body.value

    def get_transaction_data(self, days_ago=90):

        result_json = {}
        current_file_path = os.path.abspath(__file__)
        project_root = os.path.abspath(os.path.join(current_file_path, '..', '..'))
        output_dir = os.path.join(project_root, 'output')
        output_file = f'{output_dir}/output-{int(time.time())}'

        if not os.path.isfile(output_file):
            with open(output_file, "w") as json_file:
                json.dump({}, json_file)
        try:
            params = ParamsOfQueryCollection(
                collection='transactions',
                filter={'account_addr': {'eq': self.contract_address}},
                result='id, in_msg'
            )

            result = self.client.net.query_collection(params=params)

            for transaction in result.result:
                print("Transaction ID:", transaction['id'])
                in_msg_id = transaction['in_msg']

                msg_params = ParamsOfQueryCollection(
                    collection='messages',
                    filter={'id': {'eq': in_msg_id}},
                    result='src, value, boc'
                )

                msg_result = self.client.net.query_collection(params=msg_params)
                if msg_result.result:
                    msg_data = msg_result.result[0]
                    # print("Source address:", msg_data['src'])
                    # print("Value:", msg_data['value'])

                    # Parse the full BOC to extract the message body
                    parse_params = ParamsOfParse(boc=msg_data['boc'])
                    parsed_message = self.client.boc.parse_message(params=parse_params)

                    # Extract the message body
                    start_date = int((datetime.datetime.now() - datetime.timedelta(days=days_ago)).timestamp())
                    result_rates = self.call_get_rate(to_timestamp=parsed_message.parsed['created_at'], from_timestamp=start_date)
                    price = int(result_rates['value1'][1])*1000/int(result_rates['value1'][0])
                    print(f'Price: {price} \n')

                    result_json[transaction['id']] = price

        except Exception as e:
            print("Error:", e)

        with open(output_file, "w") as json_file:
            json.dump(result_json, json_file)

