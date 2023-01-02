// "SPDX-License-Identifier: 1"
pragma solidity ^0.8.7;

contract sebita_ico {
    uint public max_ankcoins = 1000000;
    uint public usd_to_ankcoins = 1000; //1 usd = 1000 ankcoins
    uint public total_ankcoins_bought = 0;

    //Vamos a hacer una especie de map de array de JS.
    //Ingresa un parámetro del tipo address,
    //y se devuelve un uint con nombre equity_ankcoins,
    //que corresponde al patrimonio de ankcoins del inversor
    mapping(address => uint) equity_ankcoins;

    //Lo mismo que arriba pero se devuelve el patrimonio equivalente en usd
    mapping(address => uint) equity_usd;
 
    //Este modifier es como una especie de middleware que chequea un 
    //requisito previo a la ejecución de una función
    modifier can_buy_ankcoins(uint usd_invested) {
        require (usd_invested * usd_to_ankcoins + total_ankcoins_bought <= max_ankcoins);
        _;
    }

    //function que me devuelve la cantidad de ankcoins de un address
    //Con "external" estamos diciendo que esta variable es una constante y es externa al contract
    //Por otro lado le colocamos un "view" informando que no cambiará ninguna variable, por eso es una "vista" nomás.
    function equity_in_ankcoins (address investor_addr) external view returns (uint) {
        return equity_ankcoins[investor_addr];
    }

    //Función que me devuelve el patrimonio en usd
    function equity_in_usd (address investor_addr) external view returns (uint) {
        return equity_usd[investor_addr];
    }

    //Función para comprar ankcoins
    //No vamos a retornar nada, sólo vamos a modificar las variables existentes.
    //Además se usa el middleware can_buy_ankcoins (que es un modifier)
    function buy_ankcoins (address investor_addr, uint usd_invested) external
    can_buy_ankcoins(usd_invested) {
        uint ankcoins_bought = usd_invested * usd_to_ankcoins;
        equity_ankcoins[investor_addr] += ankcoins_bought;
        equity_usd[investor_addr] = equity_ankcoins[investor_addr] / 1000;
        total_ankcoins_bought += ankcoins_bought;
    }

    function sell_ankcoins (address investor_addr, uint ankcoins_sold) external {
        equity_ankcoins[investor_addr] -= ankcoins_sold;
        equity_usd[investor_addr] = equity_ankcoins[investor_addr] / 1000;
        total_ankcoins_bought -=ankcoins_sold;
    }
}