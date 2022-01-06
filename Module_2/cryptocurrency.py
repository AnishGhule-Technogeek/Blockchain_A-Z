import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# PART 1 - Building a blockchain
class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []  # Transactions list should be before create_block()
        self.create_block(proof=1, prev_hash="0")  # Genesis Block
        self.nodes = set()  # Order of nodes does not matter

    # create_block function will create a block and add it to the chain
    def create_block(self, proof, prev_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prev_hash': prev_hash,
                 'transactions': self.transactions
                 }
        # After original transactions are added, empty the transactions list
        self.transactions = []
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    # proof_of_work should be hard to find, and easy to verify
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - prev_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            if current_block['prev_hash'] != self.hash(prev_block):
                return False
            # proof_of_work is easy to verify, here's how:
            prev_proof = prev_block['proof']
            proof = current_block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - prev_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = current_block
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
                                  'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount
                                 })
        prev_block = self.get_prev_block()
        return prev_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes  # Network is the set of all nodes across the world, that current node is connected to
        longest_chain = None
        max_length = len(self.chain)
        endpoint = '/get_chain'

        for node in network:
            response = requests.get("http://{0}{1}".format(node, endpoint))
            if response.status_code == 200:
                chain = response.json()['chain']
                chain_length = response.json()['length']
                if chain_length > max_length and self.is_chain_valid(chain):
                    max_length = chain_length
                    longest_chain = chain

        # If the chain was replaced
        if longest_chain:
            # Update the current chain with the updated longest valid chain
            self.chain = longest_chain
            return True
        return False


# PART 2 - Creating a cryptocurrency

# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for Node on Port 5000
node_address = str(uuid4()).replace('-', '')  # As the miner mines on the node, we need a node address to give crypto to Miner

# Creating a blockchain
blockchain = Blockchain()


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    # Transactions: Reward the miner [here, hardcoded to me :) ]
    blockchain.add_transaction(sender=node_address, receiver='Anish', amount=7.12)
    # In mining, finding proof will be computational 'hard-work', given the Avalanche effect of SHA256
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof, prev_hash)

    # data = {
    response = {
        'message': 'Congrats! You just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'prev_hash': block['prev_hash']
    }

    # response = app.response_class(
    #     response=json.dumps(data),
    #     status=200,
    #     mimetype='application/json'
    # )
    #
    # return response

    return jsonify(response), 200


# Getting the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)
                }
    # response = app.response_class(
    #     response=json.dumps(response),
    #     status=200,
    #     mimetype='application/json'
    # )
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    chain = blockchain.chain
    is_chain_valid = blockchain.is_chain_valid(chain)
    if is_chain_valid:
        response = {'message': 'GTG. The Blockchain is valid!',
                    'is_chain_valid': is_chain_valid
                    }
    else:
        response = {'message': 'The Blockchain is invalid!',
                    'is_chain_valid': is_chain_valid
                    }
    return jsonify(response), 200


# Adding a transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    posted_json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in posted_json for key in transaction_keys):
        return 'Some critical keys of the transaction are missing', 400
    index = blockchain.add_transaction(posted_json['sender'], posted_json['receiver'], posted_json['amount'])
    response = {'message': 'This transaction will be added to Block#{}'.format(index)}
    return jsonify(response), 201


# PART 3 - Decentralizing the Blockchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    posted_json = request.get_json()
    nodes = posted_json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes connected. Following nodes are now in network:',
                'all_nodes': list(blockchain.nodes),
                'total_nodes': len(blockchain.nodes)}
    return jsonify(response), 201


# Consensus, as one node may have an old chain
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if not is_chain_replaced:
        response = {'message': 'All good. The chain is longest',
                    'actual_chain': blockchain.chain}
    else:
        response = {'message': 'The nodes had different chains, hence chain replaced by longest chain',
                    'new_chain': blockchain.chain}
    return jsonify(response), 200


# Running the app
app.run(host='0.0.0.0', port=5000)
