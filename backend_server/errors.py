
class ContractNotFound(Exception):
    def __init__(self):
        self.message = "Contract cannot be addressed! Please ensure that contract exists or recheck the contract address"

