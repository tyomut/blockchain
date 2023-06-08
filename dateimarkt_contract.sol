//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.5;

contract DataMarkt {
    address public owner;

	struct Datei {
        string CID;
		address kunde;
        string modellNr;
        string arbeitsGang;
        uint anzahlTx;
        uint datum;
        uint fehlerNr;
        uint preis;
        mapping(address => uint) bezahlt;
	}

    struct KundenInfo {
        uint anzahlDateien;
        uint anzahlGekauft;
        uint saldo;
    }

	uint32 public dateiAnzahl;
	mapping(string => Datei) dateiListe;
	mapping(uint32 => string) dateiIndex;

    mapping(address => KundenInfo) kundenInfo;


    constructor() {
        owner = msg.sender;
        dateiAnzahl = 0;
    }

    function neueDatei(string memory strCID,
                       string memory modellNr, 
                       string memory arbeitsGang, 
                       uint anzahlTx, 
                       uint fehlerNr,
                       uint preis) external returns(bool){
        
        Datei storage datei = dateiListe[strCID];
        datei.CID = strCID;
        datei.kunde = msg.sender;
        datei.datum = block.timestamp;
        datei.modellNr = modellNr;
        datei.arbeitsGang = arbeitsGang;
        datei.anzahlTx = anzahlTx;
        datei.fehlerNr = fehlerNr;
        datei.preis = preis;

        dateiIndex[dateiAnzahl] = datei.CID;
        dateiAnzahl++;

        kundenInfo[datei.kunde].anzahlDateien += 1;

        return true;
    }

    function meineInfo() view public returns(KundenInfo memory info) {
        info = kundenInfo[msg.sender];
    }


    function transferSaldo() public {
        require(kundenInfo[msg.sender].saldo > 0,"Kein Saldo");
        
        bool istErfolgreich = payable(msg.sender).send(kundenInfo[msg.sender].saldo);
        
        require(istErfolgreich,"Transfer abgebrochen");
        
        kundenInfo[msg.sender].saldo = 0;
    }

    function dateiInfo(uint32 index) view public returns(string memory modellNr,
                                                         string memory arbeitsGang,
                                                         uint anzahlTx,
                                                         uint datum,
                                                         uint fehlerNr,
                                                         uint preis){
       modellNr = dateiListe[dateiIndex[index]].modellNr;
       arbeitsGang = dateiListe[dateiIndex[index]].arbeitsGang;
       anzahlTx = dateiListe[dateiIndex[index]].anzahlTx;
       datum = dateiListe[dateiIndex[index]].datum;
       fehlerNr = dateiListe[dateiIndex[index]].fehlerNr;
       preis = dateiListe[dateiIndex[index]].preis;
    }

    function dateiCID(uint32 index) view public returns(string memory cid){
        Datei storage datei = dateiListe[dateiIndex[index]];

        if (datei.bezahlt[msg.sender] == 0){
            revert("Noch nicht bezahlt");
        }

        return datei.CID;
    }

    function anzahlDateien() view public returns(uint){
        return dateiAnzahl;
    }

    function kaufen(uint32 index) payable external {
        Datei storage datei = dateiListe[dateiIndex[index]];

        if(msg.value > datei.preis){
            revert("Zahlung zu hoch");
        }
        if(msg.value < datei.preis){
            revert("Zahlung zu niedrig");
        }
        
        datei.bezahlt[msg.sender] = msg.value;

        kundenInfo[datei.kunde].anzahlGekauft += 1;
        kundenInfo[datei.kunde].saldo += datei.preis;
    }




}