// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/**
 * The same contract with checks-effects-interactions respected. The only
 * difference from GameItemsBroken is the ORDER of three lines in
 * mintWithVoucher — no extra guard, no library, no additional gas of
 * consequence. Ordering is the fix.
 */
contract GameItemsFixed {
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

        // EFFECTS first: every piece of state this contract owns is settled
        // before control leaves the building.
        voucherUsed[voucher.voucherId] = true;
        balanceOf[voucher.to][voucher.itemId] += voucher.amount;

        emit ItemMinted(voucher.to, voucher.itemId, voucher.amount, voucher.voucherId);

        // INTERACTION last. Re-entry now finds voucherUsed[id] == true and
        // reverts with VoucherUsed, which is precisely the intended behaviour.
        _notifyRecipient(voucher.to, voucher.itemId, voucher.amount);
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
