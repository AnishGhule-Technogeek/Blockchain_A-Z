// Cryptocoins ICO

// Version
pragma solidity ^0.5.4;

contract cryptocoins_ICO{

    // Introducing the max number of Cryptocoins available for sale
    uint public MAX_CRYPTOCOINS = 10000000;

    // Introducing the INR to Cryptocoins conversion rate
    uint public inr_to_cryptocoins = 100;

    // Introducing the number of Cryptocoins that have been bought by the customers
    uint public total_cryptocoins_bought = 0;

    // Mapping from the investor address to its equity in Cryptocoins and INR
    mapping(address => uint) equity_cryptocoins;
    mapping(address => uint) equity_inr;

    // Checking if an investor can buy the Cryptocoins
    modifier can_buy_cryptocoins(uint inr_invested){
        require(inr_invested * inr_to_cryptocoins + total_cryptocoins_bought <= MAX_CRYPTOCOINS);
        _;
    }

    // Getting the equity in Cryptocoins of an investor
    function equity_in_cryptocoins(address investor) external constant returns (uint) {
        return equity_cryptocoins[investor];
    }

    // Getting the equity in INR of an investor
    function equity_in_inr(address investor) external constant returns (uint) {
        return equity_inr[investor];
    }

    // Buying Cryptocoins
    function buy_cryptocoins(address investor, uint inr_invested) external
    can_buy_cryptocoins(inr_invested) {
        uint cryptocoins_bought = inr_invested * inr_to_cryptocoins;
        // Update the equity_cryptocoins and equity_inr of the investor
        equity_cryptocoins[investor] += cryptocoins_bought;
        equity_inr[investor] = equity_cryptocoins[investor] / inr_to_cryptocoins;

        // Update the total_cryptocoins_bought
        total_cryptocoins_bought += cryptocoins_bought;
    }

    // Buyback of the Cryptocoins
    function sell_cryptocoins(address investor, uint cryptocoins_to_sell) external{
        uint cryptocoins_sold = cryptocoins_to_sell;
        // Update the equity_cryptocoins and corresponding equity_inr of the investor
        equity_cryptocoins[investor] -= cryptocoins_sold;
        equity_inr[investor] = equity_cryptocoins[investor] / inr_to_cryptocoins;

        // Update the total_cryptocoins_bought
        total_cryptocoins_bought -= cryptocoins_sold;
    }

}
