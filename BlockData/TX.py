

class TX():
    def __init__(self):
        self.txid = ''
        self.inputs = []
        self.outputs = []
        self.block_height = 0
        self.confirmations = 0

    def printTX(self):
        print '\nblock ', str(self.block_height), "(" + str(self.confirmations) + " confirmations)", self.txid
        print 'IN:', self.inputs
        print 'OUT:', self.outputs
        print 'primeInput:', self.primeInputAddress()

    def primeInputAddress(self):
        addresses = []
        for tx_input in self.inputs:
            addresses.append(tx_input['address'])

        return sorted(addresses)[0]

    def receivedValue(self, address):
        value = 0
        for output in self.outputs:
            if output['address'] == address:
                value += output['value']

        return value

    def receivingTX(self, address):
        received = True
        for tx_input in self.inputs:
            if tx_input['address'] == address:
                received = False

        return received

    def sentValue(self, address):
        value = 0
        for tx_input in self.inputs:
            if tx_input['address'] == address:
                value += tx_input['value']

        change = 0
        for tx_output in self.outputs:
            if tx_output['address'] == address:
                change += tx_output['value']

        return value-change

    def sendingTX(self, address):
        sending = False
        for tx_input in self.inputs:
            if tx_input['address'] == address:
                sending = True

        return sending

    def toDict(self, address):
        tx_dict = {"txid": self.txid,
                   "primeInputAddress": self.primeInputAddress(),
                   "inputs": self.inputs,
                   "outputs": self.outputs,
                   "block_height": self.block_height,
                   "confirmations": self.confirmations,
                   "receiving": self.receivingTX(address)}
        if tx_dict["receiving"] is True:
            tx_dict["receivedValue"] = self.receivedValue(address)
        else:
            tx_dict["sentValue"] = self.sentValue(address)

        return tx_dict