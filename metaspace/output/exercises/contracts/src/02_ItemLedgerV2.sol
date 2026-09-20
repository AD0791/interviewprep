// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract ItemLedgerV2 {
    error NotAuthorised(address caller);
    error ZeroAmount();

    address public immutable gameServer;

    mapping(address => mapping(uint256 => uint256)) public balanceOf;

    event ItemMinted(address indexed to, uint256 indexed itemId, uint256 amount);

    constructor(address gameServer_) {
        gameServer = gameServer_;
    }

    modifier onlyGameServer() {
        require(msg.sender == gameServer, NotAuthorised(msg.sender));
        _;
    }

    function mint(address to, uint256 itemId, uint256 amount) external onlyGameServer {
        require(amount != 0, ZeroAmount());
        balanceOf[to][itemId] += amount;
        emit ItemMinted(to, itemId, amount);
    }
}
