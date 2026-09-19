// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC1155} from "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import {ERC1155Supply} from "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title GameItems
 * @notice ERC-1155 game assets (weapons, gear, consumables) minted from
 *         backend-signed vouchers.
 *
 * ============================================================
 * THIS IS THE SINGLE MOST IMPORTANT FILE IN THE REPO.
 * ============================================================
 * The "signed voucher" (lazy mint) pattern is how essentially every Web3 game
 * backend hands a player an on-chain reward that was earned off-chain. If the
 * Tech Lead asks you one architecture question about connecting the game
 * backend to the chain, it is some version of this.
 *
 * THE FLOW
 *   1. Player completes a mission. The GAME SERVER is authoritative — it, not
 *      the chain, decides that the mission was completed. (Never put game
 *      logic on-chain: it is public, slow, and costs money per action.)
 *   2. The server builds a MintVoucher {to, id, amount, nonce, deadline} and
 *      signs it with a hot key that holds SIGNER_ROLE. Nothing is on-chain yet
 *      and nothing has been paid for.
 *   3. The player (or a relayer, if you're paying gas) submits the voucher +
 *      signature to `mintWithVoucher`. The contract recovers the signer and
 *      mints only if that signer holds SIGNER_ROLE.
 *
 * WHY EIP-712 AND NOT `keccak256(abi.encodePacked(...))` + personal_sign
 *   - The user's wallet renders named, typed fields instead of a hex blob, so
 *     they can see what they are signing. That is a real security property,
 *     not cosmetics.
 *   - The EIP-712 domain separator binds the signature to (name, version,
 *     chainId, verifyingContract). A voucher signed for Polygon mainnet
 *     cannot be replayed on Amoy, and a voucher for this contract cannot be
 *     replayed against a second deployment of the same code.
 *   - abi.encodePacked with two dynamic types is ambiguous (hash collisions
 *     across different argument splits). EIP-712 uses abi.encode, which is not.
 *
 * THE FOUR REPLAY DEFENSES — expect to be asked to enumerate these
 *   chainId ......... cross-chain replay        (in the domain separator)
 *   verifyingContract cross-deployment replay   (in the domain separator)
 *   nonce ........... same-voucher replay       (consumed below)
 *   deadline ........ indefinite validity       (checked below)
 * Miss any one of them and you have minted infinite items.
 */
contract GameItems is ERC1155, ERC1155Supply, AccessControl, EIP712, Pausable {
    using ECDSA for bytes32;

    bytes32 public constant SIGNER_ROLE = keccak256("SIGNER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    struct MintVoucher {
        address to;
        uint256 id;
        uint256 amount;
        uint256 nonce;
        uint256 deadline;
    }

    /// @dev MUST match the struct field order and types exactly, or ecrecover
    ///      silently returns the wrong address and every mint reverts with
    ///      "bad signer" while the signature itself is perfectly valid.
    bytes32 private constant MINT_VOUCHER_TYPEHASH = keccak256(
        "MintVoucher(address to,uint256 id,uint256 amount,uint256 nonce,uint256 deadline)"
    );

    /// @notice Per-account consumed nonces. Mapping rather than a counter so
    ///         vouchers can be redeemed out of order — a player who ignores
    ///         reward #3 must still be able to redeem #4.
    mapping(address account => mapping(uint256 nonce => bool used)) public nonceUsed;

    event VoucherRedeemed(address indexed to, uint256 indexed id, uint256 amount, uint256 nonce);

    error VoucherExpired(uint256 deadline, uint256 nowTs);
    error VoucherAlreadyUsed(address to, uint256 nonce);
    error InvalidSigner(address recovered);

    constructor(address admin, string memory baseUri)
        ERC1155(baseUri)
        EIP712("MetaspaceGameItems", "1")
    {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    // ---------------------------------------------------------------
    // Voucher redemption
    // ---------------------------------------------------------------

    function mintWithVoucher(MintVoucher calldata v, bytes calldata signature)
        external
        whenNotPaused
    {
        // CHECKS ------------------------------------------------------
        if (block.timestamp > v.deadline) revert VoucherExpired(v.deadline, block.timestamp);
        if (nonceUsed[v.to][v.nonce]) revert VoucherAlreadyUsed(v.to, v.nonce);

        bytes32 structHash = keccak256(
            abi.encode(MINT_VOUCHER_TYPEHASH, v.to, v.id, v.amount, v.nonce, v.deadline)
        );
        // _hashTypedDataV4 prepends "\x19\x01" + domainSeparator.
        address signer = _hashTypedDataV4(structHash).recover(signature);
        if (!hasRole(SIGNER_ROLE, signer)) revert InvalidSigner(signer);

        // EFFECTS -----------------------------------------------------
        // Burn the nonce BEFORE minting. _mint calls onERC1155Received on a
        // contract recipient, which hands control to arbitrary code. If the
        // nonce were consumed after, that callback could re-enter and redeem
        // the same voucher again. Checks-Effects-Interactions is not optional
        // here; it is the whole defense.
        nonceUsed[v.to][v.nonce] = true;

        // INTERACTIONS ------------------------------------------------
        _mint(v.to, v.id, v.amount, "");
        emit VoucherRedeemed(v.to, v.id, v.amount, v.nonce);
    }

    /// @notice Convenience for the frontend: is this voucher still redeemable?
    function voucherStatus(address to, uint256 nonce, uint256 deadline)
        external
        view
        returns (bool redeemable, string memory reason)
    {
        if (nonceUsed[to][nonce]) return (false, "used");
        if (block.timestamp > deadline) return (false, "expired");
        return (true, "");
    }

    /// @notice Exposed so the backend can build the exact same digest it signs
    ///         and assert equality in a test. Catching a typehash mismatch in
    ///         CI is far cheaper than catching it in production.
    function hashVoucher(MintVoucher calldata v) external view returns (bytes32) {
        return _hashTypedDataV4(
            keccak256(abi.encode(MINT_VOUCHER_TYPEHASH, v.to, v.id, v.amount, v.nonce, v.deadline))
        );
    }

    // ---------------------------------------------------------------
    // Admin
    // ---------------------------------------------------------------

    function pause() external onlyRole(PAUSER_ROLE) { _pause(); }
    function unpause() external onlyRole(PAUSER_ROLE) { _unpause(); }

    function setURI(string calldata newUri) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _setURI(newUri);
    }

    // ---------------------------------------------------------------
    // Required overrides (OZ v5 uses a single _update hook)
    // ---------------------------------------------------------------

    function _update(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory values
    ) internal override(ERC1155, ERC1155Supply) {
        super._update(from, to, ids, values);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
