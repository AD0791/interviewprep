// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract ItemLedgerV1 {
    mapping(address => mapping(uint256 => uint256)) public balanceOf;

    function mint(address to, uint256 itemId, uint256 amount) external {
        balanceOf[to][itemId] += amount;
    }
}
