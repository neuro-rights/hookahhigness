# SPDX-License-Identifier: MIT
# @version ^0.3.7

import interfaces.AggregatorV3Interface as AggregatorV3Interface
import interfaces.VRFCoordinatorV2Interface as VRFCoordinatorV2Interface

# @title SmartLottery
# @author jrmunchkin
# @notice This contract creates a simple lottery which will picked a random winner once the lottery end.
# The player must pay entrance fee to play the lottery, the winner win all the pot.
# @dev The constructor takes an interval (time of duration of the lottery) and and usd entrance fee (entrance fee in dollars).
# This contract implements Chainlink Keeper to trigger when the lottery must end.
# This contract implements Chainlink VRF to pick a random winner when the lottery ends.
# This contract also implements the Chainlink price feed to know the entrance fee value in ETH.

enum LotteryState:
    OPEN
    CALCULATE_WINNER

REQUEST_CONFIRMATIONS: constant(uint16) = 3
NUM_WORDS: constant(uint32) = 1
MAX_ARRAY_SIZE: constant(uint256) = 10

i_vrfCoordinator: immutable(VRFCoordinatorV2Interface)
i_ethUsdPriceFeed: immutable(AggregatorV3Interface)
i_subscriptionId: immutable(uint64)
i_gasLane: immutable(bytes32)
i_callbackGasLimit: immutable(uint32)
i_usdEntranceFee: immutable(uint256)
i_interval: immutable(uint256)
s_lotteryState: LotteryState
s_lotteryNumber: uint256
s_players: DynArray[address, 1024]
s_startTimestamp: uint256
s_lotteryBalance: HashMap[uint256, uint256]
s_lotteryWinners: HashMap[uint256, address]
s_rewardsBalance: HashMap[address, uint256]

event StartLottery:
    lotteryNumber: indexed(uint256)
    startTime: uint256

event EnterLottery:
    lotteryNumber: indexed(uint256)
    player: indexed(address)

event RequestLotteryWinner:
    lotteryNumber: indexed(uint256)
    requestId: indexed(uint256)

event WinnerLotteryPicked:
    lotteryNumber: indexed(uint256)
    winner: indexed(address)

event ClaimLotteryRewards:
    winner: indexed(address)
    amount: uint256

@external
def __init__(
    _vrfCoordinatorV2: address, 
    _subscriptionId: uint64, 
    _gasLane: bytes32, 
    _callbackGasLimit: uint32, 
    _ethUsdPriceFeed: address, 
    _usdEntranceFee: uint256,
    _interval: uint256
    ):
    """
    @notice contructor
    @param _vrfCoordinatorV2 VRF Coordinator contract address
    @param _subscriptionId Subscription Id of Chainlink VRF
    @param _gasLane Gas lane of Chainlink VRF
    @param _callbackGasLimit Callback gas limit of Chainlink VRF
    @param _ethUsdPriceFeed Price feed address ETH to USD
    @param _usdEntranceFee Entrance fee value in dollars
    @param _interval Duration of the lottery
    """
    i_vrfCoordinator = VRFCoordinatorV2Interface(_vrfCoordinatorV2)
    i_subscriptionId = _subscriptionId
    i_gasLane = _gasLane
    i_callbackGasLimit = _callbackGasLimit
    i_ethUsdPriceFeed = AggregatorV3Interface(_ethUsdPriceFeed)
    i_usdEntranceFee = _usdEntranceFee * (10 ** 18)
    i_interval = _interval
    self.s_lotteryNumber = 1
    self.s_lotteryState = LotteryState.OPEN

@external
@payable
def enterLottery():
    """
    @notice Allow user to enter the lottery by paying entrance fee
    @dev When the first player enter the lottery the duration start
    emit an event EnterLottery when player enter the lottery
    emit an event StartLottery the lottery duration start
    """
    assert self.s_lotteryState == LotteryState.OPEN, "Lottery not open"
    assert msg.value >= self.getEntranceFeeInternal(), "Not enough funds"
    assert self.isPlayerAlreadyInLotteryInternal(msg.sender) == False, "Player already in lottery"
    self.s_lotteryBalance[self.s_lotteryNumber] += msg.value
    self.s_players.append(msg.sender)
    if(len(self.s_players) == 1):
        self.s_startTimestamp = block.timestamp
        log StartLottery(self.s_lotteryNumber, self.s_startTimestamp)
    log EnterLottery(self.s_lotteryNumber, msg.sender)

@external
@view
def checkUpkeep(_checkData: Bytes[32]) -> (bool, Bytes[32]):
    """
    @notice Chainlink checkUpkeep which will check if lottery must end
    @return upkeepNeeded boolean to know if Chainlink must perform upkeep
    """
    upkeep_needed: bool = self.isLotteryMustEnd()
    return (upkeep_needed, b"\x00")

@external
def performUpkeep(calldata: Bytes[32]):
    """
    @notice Chainlink performUpkeep which will end the lottery
    @dev This function is call if upkeepNeeded of checkUpkeep is true
    Call Chainlink VRF to request a random winner
    emit an event RequestLotteryWinner when request winner is called
    """
    upkeep_needed: bool = self.isLotteryMustEnd()
    assert upkeep_needed, "Upkeep not needed"
    self.s_lotteryState = LotteryState.CALCULATE_WINNER
    requestId: uint256 = i_vrfCoordinator.requestRandomWords(i_gasLane, i_subscriptionId, REQUEST_CONFIRMATIONS, i_callbackGasLimit, NUM_WORDS)
    log RequestLotteryWinner(self.s_lotteryNumber, requestId)

@internal
def fulfillRandomWords(_requestId: uint256, _randomWords: DynArray[uint256, MAX_ARRAY_SIZE]):
    """
    @notice Picked a random winner and restart lottery
    @dev Call by the Chainlink VRF after requesting a random winner
    emit an event WinnerLotteryPicked when random winner has been picked
    """
    indexOfWinner: uint256 = _randomWords[0] % len(self.s_players)
    actualLotteryNumber: uint256 = self.s_lotteryNumber
    winner: address = self.s_players[indexOfWinner]
    self.s_lotteryWinners[actualLotteryNumber] = winner
    self.s_players = []
    self.s_lotteryState = LotteryState.OPEN
    self.s_lotteryNumber += 1
    self.s_rewardsBalance[winner] = self.s_rewardsBalance[winner] + self.s_lotteryBalance[actualLotteryNumber]
    log WinnerLotteryPicked(actualLotteryNumber, self.s_lotteryWinners[actualLotteryNumber])

@external
def rawFulfillRandomWords(_requestId: uint256, _randomWords: DynArray[uint256, MAX_ARRAY_SIZE]):
    """
    @notice In solidity, this is the equivalent of inheriting the VRFConsumerBaseV2
    Vyper doesn't have inheritance, so we just add the function here
    """
    assert msg.sender == i_vrfCoordinator.address, "Only coordinator can fulfill!"
    self.fulfillRandomWords(_requestId, _randomWords)

@external
def claimRewards():
    """
    @notice Allow user to claim his lottery rewards
    @dev emit an event ClaimLotteryRewards when user claimed his rewards
    """
    assert self.s_rewardsBalance[msg.sender] > 0, "No pending rewards"
    toTransfer: uint256 = self.s_rewardsBalance[msg.sender]
    self.s_rewardsBalance[msg.sender] = 0
    send(msg.sender, toTransfer)
    log ClaimLotteryRewards(msg.sender, toTransfer)

@internal
@view
def isLotteryMustEnd() -> bool:
    """
    @notice Check if lottery must end
    @return upkeepNeeded boolean to know if lottery must end
    @dev Lottery end when all this assertions are true :
    The lottery is open
    The lottery have at least one player
    The lottery have some balance
    The lottery duration is over
    """
    isOpen: bool = self.s_lotteryState == LotteryState.OPEN
    timePassed: bool = ((block.timestamp - self.s_startTimestamp) > i_interval)
    hasPlayers: bool = len(self.s_players) > 0
    hasBalance: bool = self.s_lotteryBalance[self.s_lotteryNumber] > 0
    upkeep_needed: bool = isOpen and timePassed and hasPlayers and hasBalance
    return upkeep_needed

@internal
@view
def isPlayerAlreadyInLotteryInternal(_user: address) -> bool:
    """
    @notice Check if the user already play the lottery
    @param _user address of the user
    @return isAllowed true if already play, false ether
    """
    if _user in self.s_players:
        return True
    return False

@internal
@view
def getEntranceFeeInternal() -> uint256:
    """
    @notice Get entrance fee to participate to the lottery
    @return entranceFee Entrance fee in ETH
    @dev Implements Chainlink price feed
    """
    a: uint80 = 0
    price: int256 = 0
    b: uint256 = 0
    c: uint256 = 0
    d: uint80 = 0
    (a,price,b,c,d) = i_ethUsdPriceFeed.latestRoundData()
    adjustedPrice: uint256 = convert(price, uint256) * 10 ** 10
    return (i_usdEntranceFee * 10 ** 18) / adjustedPrice

@external
@view
def isPlayerAlreadyInLottery(_user: address) -> bool:
    """
    @notice Check if the user already play the lottery
    @param _user address of the user
    @return isAllowed true if already play, false ether
    @dev For external call
    """
    return self.isPlayerAlreadyInLotteryInternal(_user)

@external
@view
def getEntranceFee() -> uint256:
    """
    @notice Get entrance fee to participate to the lottery
    @return entranceFee Entrance fee in ETH
    @dev Implements Chainlink price feed
    For external call
    """
    return self.getEntranceFeeInternal()

@external
@view
def getUsdEntranceFee() -> uint256:
    """
    @notice Get entrance fee in dollars to participate to the lottery
    @return usdEntranceFee Entrance fee in dollars
    """
    return i_usdEntranceFee

@external
@view
def getInterval() -> uint256:
    """
    @notice Get duration of the lottery
    @return interval Duration of the lottery
    """
    return i_interval

@external
@view
def getActualLotteryNumber() -> uint256:
    """
    @notice Get actual lottery number
    @return lotteryNumber Actual lottery number
    """
    return self.s_lotteryNumber

@external
@view
def getLotteryState() -> LotteryState:
    """
    @notice Get the state of the lottery
    @return lotteryState Lottery state
    """
    return self.s_lotteryState

@external
@view
def getPlayer(_index: uint256) -> address:
    """
    @notice Get player address with index
    @param _index Index of player
    @return player Player address
    """
    return self.s_players[_index]

@external
@view
def getNumberOfPlayers() -> uint256:
    """
    @notice Get the number of players of the lottery
    @return numPlayers Number of players
    """
    return len(self.s_players)

@external
@view
def getStartTimestamp() -> uint256:
    """
    @notice Get the timestamp when the lottery start
    @return startTimestamp Start timestamp
    """
    return self.s_startTimestamp

@external
@view
def getActualLotteryBalance() -> uint256:
    """
    @notice Get the value of rewards of the actual lottery
    @return lotteryBalance Lottery Balance
    """
    return self.s_lotteryBalance[self.s_lotteryNumber]

@external
@view
def getLotteryBalance(_lotteryNumber: uint256) -> uint256:
    """
    @notice Get the value of rewards of a specific lottery
    @param _lotteryNumber The number of the lottery
    @return lotteryBalance Lottery Balance
    """
    return self.s_lotteryBalance[_lotteryNumber]

@external
@view
def getWinner(_lotteryNumber: uint256) -> address:
    """
    @notice Get the winner of a specific lottery
    @param _lotteryNumber The number of the lottery
    @return lotteryWinner Lottery winner
    """
    return self.s_lotteryWinners[_lotteryNumber]

@external
@view
def getUserRewardsBalance(_user: address) -> uint256:
    """
    @notice Get the user pending rewards of his winning lotteries
    @param _user address of the user
    @return rewardsBalance Rewards balance
    """
    return self.s_rewardsBalance[_user]