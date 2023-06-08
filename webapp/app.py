import os
import sys

from web3 import Web3
import blockchain_helper as blockchain
from data_helper import ContractInfo, MeineInfo
from werkzeug.wsgi import  wrap_file

# Flask
from flask import Flask, request, render_template, send_file
#from gevent.pywsgi import WSGIServer

config = {
    # "DEBUG": True
}
flaskapp = Flask(__name__)
flaskapp.config.from_mapping(config)


web3_provider = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

contract_info: ContractInfo = ContractInfo.loadContractInfo()

active_account = ""
active_account_index = 0
active_account_balance = 0
anzahl_dateien = 0
datei_liste = []
contract = None
meine_info = None
file = None

if contract_info is not None:
    contract = blockchain.getContract(w3 = web3_provider, 
                                      contract_address = contract_info.contract_address, 
                                      contract_abi = contract_info.contract_abi)
    if contract is not None:
        try:
            anzahl_dateien = blockchain.getAnzahlContractDateien(dateimarkt_contract = contract)
            if anzahl_dateien is None:
                contract_info = None    
                anzahl_dateien = ""
        except:
            contract_info = None

if contract_info is not None:
    datei_liste = blockchain.getDateiListe(dateimarkt_contract = contract)

@flaskapp.route("/", methods=["GET","POST"])
def index():
    global active_account, active_account_index, active_account_balance
    global contract, contract_info, anzahl_dateien, datei_liste, meine_info, file

    txReceipt = None
    datei_idx = None

    if request.method == "POST":
        if request.form.get("action") == "deploy":
            if contract_info is None:
                contract_info, txReceipt = blockchain.deployContract(web3_provider)

                contract = blockchain.getContract(w3 = web3_provider, 
                                                  contract_address = contract_info.contract_address, 
                                                  contract_abi = contract_info.contract_abi
                                                  )

        if request.form.get("action") == "select-customer":
           active_account_index = int(request.form.get("active_account_index"))
           active_account, active_account_balance = blockchain.getAccount(web3_provider,
                                                                          active_account_index
                                                                          )
           meine_info = blockchain.getMeineInfo(w3 = web3_provider, 
                                                contract_info = contract_info,
                                                account = active_account
                                                )
           
        if request.form.get("action") == "upload-file":
            cid, txHash = blockchain.addNeueDatei(account = active_account,
                                                  dateimarkt_contract = contract, 
                                                  fileName = request.files["file"].filename, 
                                                  file = request.files["file"],
                                                  modellNr = request.form.get("modellNr"),
                                                  arbeitsGang = request.form.get("arbeitsGang"),
                                                  anzahlTx = int(request.form.get("anzahlTx")),
                                                  fehlerNr = int(request.form.get("fehlerNr")),
                                                  preis = int(request.form.get("preis")),
                                                 )
            
            txReceipt = blockchain.getReceipt(w3 = web3_provider, 
                                              txHash = txHash
                                              )
            
            txReceipt = dict(txReceipt)
            txReceipt["cid"] = cid

            anzahl_dateien = blockchain.getAnzahlContractDateien(dateimarkt_contract = contract)
            
            active_account, active_account_balance = blockchain.getAccount(web3_provider,
                                                                           active_account_index
                                                                           )

            datei_liste = blockchain.getDateiListe(dateimarkt_contract = contract)

        if request.form.get("action") == "kaufen":
            if request.form.get('datei_id') is not None:
                datei_idx = int(request.form.get('datei_id'))

                txHash, file = blockchain.dateiKaufen(dateimarkt_contract = contract, 
                                                account = active_account, 
                                                datei_idx = datei_idx
                                                )

                txReceipt = blockchain.getReceipt(w3 = web3_provider,
                                                txHash = txHash
                                                )

                active_account, active_account_balance = blockchain.getAccount(web3_provider,
                                                                               active_account_index
                                                                              )
                
        if request.form.get("action") == "transfer":
                if meine_info.saldo != 0:
                    txHash = blockchain.transferSaldo(dateimarkt_contract = contract, 
                                                    account = active_account
                                                    )

                    txReceipt = blockchain.getReceipt(w3 = web3_provider,
                                                    txHash = txHash
                                                    )

                    active_account, active_account_balance = blockchain.getAccount(web3_provider,
                                                                                active_account_index
                                                                                )

                    meine_info = blockchain.getMeineInfo(w3 = web3_provider, 
                                                        contract_info = contract_info,
                                                        account = active_account
                                                        )
        if request.form.get("action") == "download":
            datei_idx =  request.form.get("datei_idx")
            if file is not None:
                return send_file(file, as_attachment= True,  mimetype="text/csv", download_name=f"Datei_{datei_idx}.csv")                

    return render_template("index.html",active_account = active_account, 
                                        active_account_index = active_account_index, 
                                        active_account_balance = active_account_balance,
                                        contract_info = contract_info,
                                        anzahl_dateien = anzahl_dateien,
                                        txReceipt = txReceipt,
                                        datei_liste = datei_liste,
                                        meine_info = meine_info,
                                        datei_idx = datei_idx
                                        )


if __name__ == "__main__":
    flaskapp.run(port=5000, threaded=False)
    #http_server = WSGIServer(('0.0.0.0', 5000), app)
    #http_server.serve_forever()