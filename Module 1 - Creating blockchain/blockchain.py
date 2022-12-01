import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockhain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof, #proof is nonce
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        return block

    def get_previous_block (self):
        return self.chain[-1]
    
    def hash_operation(self, current_proof, previous_proof):
        # hashlib.sha256(str(previous_proof**2 - new_proof**2).encode()).hexdigest()
        # output => 6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b
        return hashlib.sha256(str(previous_proof**2 - current_proof**2).encode()).hexdigest()

    def proof_of_work(self, previous_proof):
        current_proof = 1  # We will increment this 1 by 1 until we get the
        # right hash
        check_proof = False
        while check_proof is False:
            hash_operation = self.hash_operation(current_proof, previous_proof)
            if hash_operation[:4] == '0000': #Four leading zeros
                print(hash_operation)
                check_proof = True
            else:
                current_proof += 1
        return current_proof
    
    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode() #es como JSON.stringify, convertimos al dict
        #en formato JSON y ordenamos las keys en orden alfabético.
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid (self):
        previous_block = self.chain[0]
        block_index = 1
        while block_index < len(self.chain):
            current_block = self.chain[block_index]
            if current_block['previous_hash'] != self.hash_block(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = current_block['proof']
            current_hash = self.hash_operation(proof, previous_proof)
            if current_hash[:4] != '0000':
                return False
            previous_block = current_block
            block_index += 1
        return True

#Creating webapp    
app = Flask(__name__)

#Creating blockchain
blockchain = Blockhain()

@app.route('/mine-block', methods =['GET'])
def mine_block():
    prev_block = blockchain.get_previous_block()#get the last block before adding new one
    prev_proof = prev_block['proof']
    print(prev_proof)
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash_block(prev_block)
    block_created = blockchain.create_block(proof, prev_hash)
    response = {
        'message': "Block mined successfully",
        'data': {
            'index': block_created['index'],
            'timestamp': block_created['timestamp'],
            'proof': block_created['proof'], #proof is nonce
            'previous_hash': block_created['previous_hash']
            }
        }
    return jsonify(response), 200

@app.route('/blockchain', methods =['GET'])
def get_blockchain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
        }
    return jsonify(response), 200

@app.route('/check-valid-blockchain', methods =['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid()
    response = {
            'is_valid': is_valid
        }
    return jsonify(response), 200

app.run(host='0.0.0.0', port='5000' )
    