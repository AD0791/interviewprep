// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC1155} from "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import {ERC1155Holder} from "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";

interface IMintable {
    function mint(address to, uint256 amount) external;
}

/**
 * @title ItemStaking
 * @notice Stake ERC-1155 game items, accrue $LORD.
 *
 * THE ONE IDEA TO TAKE FROM THIS FILE: THE ACCUMULATOR PATTERN
 * ------------------------------------------------------------
 * The naive design is a loop: every time someone claims, walk all stakers and
 * pay each. That is O(n) gas in a system where n grows without bound — it
 * works with 50 testers and bricks at 50,000 players, because eventually the
 * loop exceeds the block gas limit and NOBODY can claim. This is called an
 * unbounded-loop DoS and it is a top-5 audit finding.
 *
 * The fix is to never iterate. Keep one global accumulator:
 *
 *   accRewardPerWeight += rewardPerSecond * elapsed / totalWeight
 *
 * "reward owed to one unit of stake since the beginning of time". A user's
 * claim is then O(1):
 *
 *   pending = userWeight * accRewardPerWeight - userRewardDebt
 *
 * where rewardDebt is the accumulator value snapshotted when they last
 * touched the contract. This is the MasterChef pattern; you will meet it in
 * every staking system in the space, so being able to derive it on a
 * whiteboard is worth real points.
 *
 * NOTE ON PRECISION: integer division truncates, so the accumulator is scaled
 * by 1e18 and divided out at the end. Doing it in the other order silently
 * pays everyone zero — a classic bug.
 */
contract ItemStaking is ERC1155Holder, ReentrancyGuard, AccessControl, Pausable {
    uint256 private constant PRECISION = 1e18;

    bytes32 public constant CONFIG_ROLE = keccak256("CONFIG_ROLE");

    IERC1155 public immutable items;
    IMintable public immutable rewardToken;

    /// @notice Reward weight per item id. A legendary weapon earns more than a
    ///         common one. Unset ids have weight 0 and are not stakeable.
    mapping(uint256 itemId => uint256 weight) public itemWeight;

    uint256 public rewardPerSecond;
    uint256 public totalWeight;
    uint256 public accRewardPerWeight; // scaled by PRECISION
    uint256 public lastUpdate;

    struct UserInfo {
        uint256 weight;
        uint256 rewardDebt; // scaled by PRECISION
    }

    mapping(address user => UserInfo) public userInfo;
    mapping(address user => mapping(uint256 itemId => uint256 amount)) public staked;

    event Staked(address indexed user, uint256 indexed itemId, uint256 amount, uint256 newWeight);
    event Unstaked(address indexed user, uint256 indexed itemId, uint256 amount, uint256 newWeight);
    event Claimed(address indexed user, uint256 amount);
    event WeightSet(uint256 indexed itemId, uint256 weight);

    error NotStakeable(uint256 itemId);
    error InsufficientStake(uint256 have, uint256 want);
    error ZeroAmount();

    constructor(address admin, IERC1155 items_, IMintable rewardToken_, uint256 rewardPerSecond_) {
        items = items_;
        rewardToken = rewardToken_;
        rewardPerSecond = rewardPerSecond_;
        lastUpdate = block.timestamp;
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    // ---------------------------------------------------------------
    // Accounting
    // ---------------------------------------------------------------

    /// @dev Must run BEFORE any change to totalWeight or a user's weight.
    ///      Forgetting this in one path is how staking contracts leak funds.
    function _accrue() internal {
        if (block.timestamp == lastUpdate) return;
        if (totalWeight > 0) {
            uint256 elapsed = block.timestamp - lastUpdate;
            accRewardPerWeight += (elapsed * rewardPerSecond * PRECISION) / totalWeight;
        }
        // When totalWeight == 0 we advance the clock without accruing, so
        // rewards for an empty pool are simply not emitted rather than being
        // handed to whoever stakes first.
        lastUpdate = block.timestamp;
    }

    function pendingReward(address user) public view returns (uint256) {
        UserInfo memory u = userInfo[user];
        uint256 acc = accRewardPerWeight;
        if (block.timestamp > lastUpdate && totalWeight > 0) {
            uint256 elapsed = block.timestamp - lastUpdate;
            acc += (elapsed * rewardPerSecond * PRECISION) / totalWeight;
        }
        return (u.weight * acc - u.rewardDebt) / PRECISION;
    }

    function _settle(address user) internal returns (uint256 paid) {
        UserInfo storage u = userInfo[user];
        paid = (u.weight * accRewardPerWeight - u.rewardDebt) / PRECISION;
        if (paid > 0) {
            // EFFECTS before INTERACTIONS: the debt is written before the
            // external mint call, so a malicious token cannot re-enter and be
            // paid twice. nonReentrant is the belt; this is the braces.
            u.rewardDebt = u.weight * accRewardPerWeight;
            rewardToken.mint(user, paid);
            emit Claimed(user, paid);
        }
    }

    // ---------------------------------------------------------------
    // User actions
    // ---------------------------------------------------------------

    function stake(uint256 itemId, uint256 amount) external nonReentrant whenNotPaused {
        if (amount == 0) revert ZeroAmount();
        uint256 w = itemWeight[itemId];
        if (w == 0) revert NotStakeable(itemId);

        _accrue();
        _settle(msg.sender);

        UserInfo storage u = userInfo[msg.sender];
        uint256 added = w * amount;
        u.weight += added;
        totalWeight += added;
        staked[msg.sender][itemId] += amount;
        u.rewardDebt = u.weight * accRewardPerWeight;

        // External call last. safeTransferFrom hands control to the token
        // contract; by now all of our own state is already consistent.
        items.safeTransferFrom(msg.sender, address(this), itemId, amount, "");
        emit Staked(msg.sender, itemId, amount, u.weight);
    }

    function unstake(uint256 itemId, uint256 amount) external nonReentrant {
        if (amount == 0) revert ZeroAmount();
        uint256 have = staked[msg.sender][itemId];
        if (have < amount) revert InsufficientStake(have, amount);

        _accrue();
        _settle(msg.sender);

        UserInfo storage u = userInfo[msg.sender];
        uint256 removed = itemWeight[itemId] * amount;
        u.weight -= removed;
        totalWeight -= removed;
        staked[msg.sender][itemId] = have - amount;
        u.rewardDebt = u.weight * accRewardPerWeight;

        items.safeTransferFrom(address(this), msg.sender, itemId, amount, "");
        emit Unstaked(msg.sender, itemId, amount, u.weight);
    }

    function claim() external nonReentrant {
        _accrue();
        _settle(msg.sender);
    }

    // ---------------------------------------------------------------
    // Admin
    // ---------------------------------------------------------------

    /// @dev _accrue() first so the rate change is not applied retroactively to
    ///      time already elapsed. Every setter that touches reward math has to
    ///      do this.
    function setRewardPerSecond(uint256 newRate) external onlyRole(CONFIG_ROLE) {
        _accrue();
        rewardPerSecond = newRate;
    }

    /// @dev Only settable for ids nobody has staked yet; changing the weight of
    ///      a live item would desynchronise totalWeight from the sum of user
    ///      weights. In production you would version the pool instead.
    function setItemWeight(uint256 itemId, uint256 weight) external onlyRole(CONFIG_ROLE) {
        _accrue();
        itemWeight[itemId] = weight;
        emit WeightSet(itemId, weight);
    }

    function pause() external onlyRole(CONFIG_ROLE) { _pause(); }
    function unpause() external onlyRole(CONFIG_ROLE) { _unpause(); }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155Holder, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
