from web3 import Web3
from solcx import compile_files

from data_helper import ContractInfo, MeineInfo, ContractDatei
import ipfs_helper

CONTRACT_DEFINITION_FILE = "dateimarkt_contract.sol"

def getAccount(w3, index):
    active_account = w3.eth.accounts[index]

    active_account_balance = Web3.from_wei(w3.eth.get_balance(active_account),"ether")

    return active_account, active_account_balance

def deployContract(w3):
    contract_owner = w3.eth.default_account = w3.eth.accounts[0]

    compiled_sol = compile_files([CONTRACT_DEFINITION_FILE],output_values=["abi", "bin"])
    contract_id, contract_interface = compiled_sol.popitem()
    bytecode = contract_interface["bin"]
    contract_abi = contract_interface["abi"]

    DateiMarkt = w3.eth.contract(abi=contract_abi, bytecode=bytecode)

    txHash = DateiMarkt.constructor().transact()

    txReceipt = w3.eth.wait_for_transaction_receipt(txHash)

    contract_address = txReceipt.contractAddress

    contract_info = ContractInfo(contract_owner,
                                 contract_address, 
                                 txHash.hex(),
                                 contract_abi)

    contract_info.save()

    return contract_info, txReceipt

def getContract(w3, contract_address, contract_abi) :
    contract = None
    try:
        contract = w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )
    except:
        pass

    return contract

def getMeineInfo(w3, contract_info, account):
    w3.eth.default_account = account

    contract = getContract(w3 = w3, 
                           contract_address = contract_info.contract_address, 
                           contract_abi = contract_info.contract_abi
                          )

    anzahlDateien, anzahlGekauft, saldo = contract.functions.meineInfo().call()
    
    return MeineInfo(anzahlDateien, anzahlGekauft, saldo)

def getAnzahlContractDateien(dateimarkt_contract):
    return dateimarkt_contract.functions.anzahlDateien().call()

def addNeueDatei(account, dateimarkt_contract, fileName, file, modellNr, arbeitsGang, anzahlTx, fehlerNr, preis):
    if dateimarkt_contract is None:
        return None
    
    response_dict = ipfs_helper.ipfs_upload(fileName, file) # Name, Hash, Size
    
    cid = str(response_dict["Hash"])

    txHash = dateimarkt_contract.functions.neueDatei(cid, modellNr, arbeitsGang, anzahlTx, fehlerNr, Web3.to_wei(preis,"ether")).transact({"from":account})

    if not txHash:
        raise Exception("Neue Datei konnte nicht hinzugefügt werden.")

    return cid, txHash

def getReceipt(w3, txHash):
    return w3.eth.get_transaction(txHash)
    
def getDateiInfo(dateimarkt_contract, idx):
    datei_info = dateimarkt_contract.functions.dateiInfo(idx).call()

    return ContractDatei(idx = idx, 
                         modellNr = datei_info[0],
                         arbeitsGang = datei_info[1],
                         anzahlTx = datei_info[2],
                         datum = datei_info[3],
                         fehlerNr = datei_info[4],
                         preis = datei_info[5])

def getDateiListe(dateimarkt_contract):
    anzahlDateien = getAnzahlContractDateien(dateimarkt_contract=dateimarkt_contract)

    datei_liste = []

    for idx in range(0,anzahlDateien):
        contract_datei = getDateiInfo(dateimarkt_contract = dateimarkt_contract, idx = idx)

        datei_liste.append(contract_datei)        

    return datei_liste

def dateiKaufen(dateimarkt_contract, account, datei_idx):
    contract_datei = getDateiInfo(dateimarkt_contract = dateimarkt_contract, idx = datei_idx)

    txHash = dateimarkt_contract.functions.kaufen(datei_idx).transact({"from":account,"value": contract_datei.preis})

    if not txHash:
        raise Exception("Datei konnte nicht gekauft werden.")

    datei_cid = dateimarkt_contract.functions.dateiCID(datei_idx).call()

    file = ipfs_helper.ipfs_download(cid=datei_cid)

    return txHash, file

def transferSaldo(dateimarkt_contract, account):
    
    txHash = dateimarkt_contract.functions.transferSaldo().transact({"from":account})

    if not txHash:
        raise Exception("Datei konnte nicht gekauft werden.")

    return txHash
