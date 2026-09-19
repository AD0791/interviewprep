// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title LordToken
 * @notice In-game reward currency (the $LORD analogue).
 *
 * INTERVIEW TALKING POINTS
 * ------------------------
 * 1. Why a capped supply + MINTER_ROLE instead of `Ownable`?
 *    Role-based access lets you give the staking contract minting rights
 *    without giving it upgrade/withdraw rights. Least privilege. `Ownable`
 *    collapses every privilege into one key — a single compromise is total.
 *
 * 2. Why ERC20Permit (EIP-2612)?
 *    A player should not need MATIC to approve a spend. `permit()` takes an
 *    off-chain signature and sets the allowance inside the same transaction
 *    the relayer pays for. This is the gasless-UX primitive for ERC-20;
 *    ERC-2771 / ERC-4337 are the more general versions.
 *
 * 3. Why cap the supply on-chain rather than in the backend?
 *    Because the backend is not a trust boundary. Anything the tokenomics
 *    promise and the chain does not enforce is a promise, not a guarantee.
 */
contract LordToken is ERC20, ERC20Permit, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    uint256 public immutable maxSupply;

    error MaxSupplyExceeded(uint256 requested, uint256 remaining);

    constructor(address admin, uint256 maxSupply_)
        ERC20("Lord", "LORD")
        ERC20Permit("Lord")
    {
        maxSupply = maxSupply_;
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    /// @notice Mint rewards. Only the staking contract / reward distributor holds MINTER_ROLE.
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        uint256 remaining = maxSupply - totalSupply();
        if (amount > remaining) revert MaxSupplyExceeded(amount, remaining);
        _mint(to, amount);
    }
}
