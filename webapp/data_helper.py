import dataclasses
import json

CONTRACT_INFO_FILE = "contract_info.json"

@dataclasses.dataclass
class ContractInfo:
    contract_owner: str
    contract_address: str
    contract_transaction: str
    contract_abi: str

    @classmethod
    def from_json(self, json_str):
        data: dict = json.loads(json_str)
        return self(data["contract_owner"],
                    data["contract_address"],
                    data["contract_transaction"],
                    data["contract_abi"],
                    )

    def to_json(self):
        return json.dumps(self, default= lambda o: o.__dict__)
    
    @classmethod
    def loadContractInfo(self):
        try:
            f = open(CONTRACT_INFO_FILE,"r")
            return ContractInfo.from_json(f.read())
        except FileNotFoundError:
            return None
        except Exception as ex:
            raise(ex)

    def save(self):
        f = open(CONTRACT_INFO_FILE,"w")
        f.write(self.to_json())
    

@dataclasses.dataclass
class MeineInfo:
    anzahl_dateien: int
    anzahl_gekauft: int
    saldo: int

@dataclasses.dataclass
class ContractDatei:
    idx: int
    modellNr: str
    arbeitsGang: str
    anzahlTx: int
    datum: int
    fehlerNr: int
    preis: int


