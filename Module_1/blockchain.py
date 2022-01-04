import datetime
import hashlib
import json
from flask import Flask, jsonify


# Part 1 - Building a blockchain
class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(proof=1, prev_hash="0")  # Genesis Block

    # create_block function will create a block and add it to the chain
    def create_block(self, proof, prev_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prev_hash': prev_hash
                 }
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


# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a blockchain
blockchain = Blockchain()


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    # In mining, finding proof will be computational 'hard-work', given the Avalanche effect of SHA256
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof, prev_hash)

    # data = {
    response = {
        'message': 'Congrats! You just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
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


# Running the app
app.run(host='0.0.0.0', port=5000)
