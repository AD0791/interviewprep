// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract ItemLedgerV3 {
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
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
        if (_recover(digest, signature) != signer) revert BadSignature();

        voucherUsed[voucher.voucherId] = true;
        balanceOf[voucher.to][voucher.itemId] += voucher.amount;

        emit ItemMinted(voucher.to, voucher.itemId, voucher.amount, voucher.voucherId);
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
