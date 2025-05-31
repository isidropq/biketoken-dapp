// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./DBSTEToken.sol";
contract BikeStation {
    DBSTEToken public immutable token;
    uint256 public constant TOKENS_PER_KM = 1 ether;
    constructor(DBSTEToken _token) { token = _token; }
    function mintForDistance(uint256 km) external {
        require(km>0,"zero-distance");
        token.mint(msg.sender, km * TOKENS_PER_KM);
    }
}
