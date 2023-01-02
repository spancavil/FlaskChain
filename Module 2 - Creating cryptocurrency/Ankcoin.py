import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


#See the environments and modules of the environment
#conda info --envs
#pip list

class Blockhain:
    def __init__(self):
        self.chain = []
        self.mem_pool = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set() # We need the nodes will not repeat. The node will
        #contain a set of directions (IP) of all nodes.
        #These nodes will be running on different servers.

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof, #proof is the golden nonce
            'previous_hash': previous_hash,
            'mem_pool': self.mem_pool,
        }
        self.mem_pool = [] #we empty the mem_pool after mining the block
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
    
    def is_chain_valid (self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
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
    
    def add_tx (self, sender, receiver, amount):
        self.mem_pool.append({
                sender, receiver, amount
            })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) #Lo que se hace básicamente en
        #parsed_url es tomar la dirección y en netloc se asigna: IP:PORT
        #pero sin HTTP
    
    def replace_chain (self):
        network = self.nodes
        longest_chain = None
        max_len = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/blockchain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if (length > max_len) and self.is_chain_valid(chain):
                    max_len = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

#Creating webapp    
app = Flask(__name__)

#Creating blockchain
blockchain = Blockhain()

#Generate address for node
address = str(uuid4()).replace('-', '')

@app.route('/mine-block', methods =['GET'])
def mine_block():
    prev_block = blockchain.get_previous_block()#get the last block before adding new one
    prev_proof = prev_block['proof']
    print(prev_proof)
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash_block(prev_block)
    blockchain.add_tx(sender = address, receiver = 'Sebas', amount = 10)
    block_created = blockchain.create_block(proof, prev_hash)
    response = {
        'message': "Block mined successfully",
        'data': {
            'index': block_created['index'],
            'timestamp': block_created['timestamp'],
            'proof': block_created['proof'], #proof is nonce
            'previous_hash': block_created['previous_hash'],
            'transactions': block_created['transactions'],
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

@app.route('/replace_chain', methods =['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
                'is_chain_replaced': is_chain_replaced,
                'new_chain': blockchain.chain
            }
    else:
        response = {
                'is_chain_replaced': is_chain_replaced,
                'actual_chain': blockchain.chain
            }
    return jsonify(response), 200

@app.route('/add_transaction', methods =['POST'])
def add_tx():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_tx(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to the block number: {index}'}
    return jsonify(response), 201 #201 is created

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No nodes", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'All the nodes are now connected',
        'total_nodes': list(blockchain.nodes)
        }
    return jsonify(response), 201    
