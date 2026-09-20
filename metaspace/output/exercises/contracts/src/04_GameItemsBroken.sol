// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/**
 * DELIBERATELY BROKEN. This is level 11's exhibit, not a contract to copy.
 *
 * It is the voucher mint from ItemLedgerV3 with one change: the voucher is
 * marked used AFTER the recipient callback instead of before. Everything else
 * — the signature check, the deadline, the replay mapping — is identical and
 * correct, which is exactly what makes the bug hard to see in review.
 */
contract GameItemsBroken {
    error BadSignature();
    error VoucherUsed(uint256 voucherId);
    error VoucherExpired(uint256 deadline);

    struct Voucher {
        address to;
        uint256 itemId;
        uint256 amount;
        uint256 voucherId;
        uint256 deadline;
    }

    bytes32 private constant VOUCHER_TYPEHASH = keccak256(
        "Voucher(address to,uint256 itemId,uint256 amount,uint256 voucherId,uint256 deadline)"
    );

    bytes32 private immutable DOMAIN_SEPARATOR;
    address public immutable signer;

    mapping(address => mapping(uint256 => uint256)) public balanceOf;
    mapping(uint256 => bool) public voucherUsed;

    event ItemMinted(address indexed to, uint256 indexed itemId, uint256 amount, uint256 voucherId);

    constructor(address signer_) {
        signer = signer_;
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes("Metaspace Items")),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );
    }

    function mintWithVoucher(Voucher calldata voucher, bytes calldata signature) external {
        if (block.timestamp > voucher.deadline) revert VoucherExpired(voucher.deadline);
        if (voucherUsed[voucher.voucherId]) revert VoucherUsed(voucher.voucherId);
        if (_recover(_digest(voucher), signature) != signer) revert BadSignature();

        balanceOf[voucher.to][voucher.itemId] += voucher.amount;

        // ERC-1155 requires notifying a contract recipient that it received
        // tokens. That notification is a call into code the recipient wrote.
        _notifyRecipient(voucher.to, voucher.itemId, voucher.amount);

        // THE BUG. Control has already been handed to the recipient above, and
        // when it re-enters, voucherUsed[id] is still false.
        voucherUsed[voucher.voucherId] = true;

        emit ItemMinted(voucher.to, voucher.itemId, voucher.amount, voucher.voucherId);
    }

    function _notifyRecipient(address to, uint256 id, uint256 amount) private {
        if (to.code.length == 0) return;
        (bool ok, ) = to.call(
            abi.encodeWithSignature(
                "onERC1155Received(address,address,uint256,uint256,bytes)",
                msg.sender,
                address(0),
                id,
                amount,
                ""
            )
        );
        require(ok, "recipient rejected");
    }

    function _digest(Voucher calldata voucher) private view returns (bytes32) {
        bytes32 structHash = keccak256(
            abi.encode(
                VOUCHER_TYPEHASH,
                voucher.to,
                voucher.itemId,
                voucher.amount,
                voucher.voucherId,
                voucher.deadline
            )
        );
        return keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
    }

    function _recover(bytes32 digest, bytes calldata signature) private pure returns (address) {
        if (signature.length != 65) revert BadSignature();
        bytes32 r = bytes32(signature[0:32]);
        bytes32 s = bytes32(signature[32:64]);
        uint8 v = uint8(signature[64]);
        if (uint256(s) > 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0) {
            revert BadSignature();
        }
        address recovered = ecrecover(digest, v, r, s);
        if (recovered == address(0)) revert BadSignature();
        return recovered;
    }
}
