# SPDX-License-Identifier: MIT
# @version ^0.3.7

import interfaces.AggregatorV3Interface as AggregatorV3Interface
import interfaces.VRFCoordinatorV2Interface as VRFCoordinatorV2Interface

# @title SmartLotteryV2
# @author jrmunchkin
# @notice This contract creates a ticket lottery which will picked a random winning ticket once the lottery end.
# The player must buy tickets to play the lottery, he also must pay fee everytime buying a ticket.
# The lottery works like so :
# - The pot is divided into 4 pots. The size of each pot is based on a percentage set in the constructor.
# - Everytime the user buy a ticket he get 4 random numbers. Maximum buying ticket : 10 per user per lottery.
# - If the user has a ticket with the first number matching the winning ticket he win the smallest pot.
# - If the user has a ticket with the two first number matching the winning ticket he win the second pot.
# - If the user has a ticket with the third first number matching the winning ticket he win the third pot.
# - If the user has a ticket with the fourth number matching the winning ticket he win the biggest pot.
# - Each pot is also divided by the number of user who win it.
# @dev The constructor takes an interval (time of duration of the lottery), an usd entrance fee (entrance fee in dollars)
# and a prize distribution corresponding on the percentage of each pots.
# This contract implements Chainlink Keeper to trigger when the lottery must end.
# This contract implements Chainlink VRF to pick a random winning ticket when the lottery ends.
# This contract also implements the Chainlink price feed to know the ticket fee value in ETH.

enum LotteryState:
    OPEN
    DRAW_WINNING_TICKET

REQUEST_CONFIRMATIONS: constant(uint16) = 3
NUM_WORDS: constant(uint32) = 4
MAX_BUYING_TICKET: constant(uint256) = 10
MAX_ARRAY_SIZE: constant(uint256) = 10

i_vrfCoordinator: immutable(VRFCoordinatorV2Interface)
i_ethUsdPriceFeed: immutable(AggregatorV3Interface)
i_subscriptionId: immutable(uint64)
i_gasLane: immutable(bytes32)
i_callbackGasLimit: immutable(uint32)
i_usdTicketFee: immutable(uint256)
i_interval: immutable(uint256)
s_lotteryState: LotteryState
s_lotteryNumber: uint256
s_randNonce: uint256
s_players: DynArray[address, 1024]
s_startTimestamp: uint256
s_prizeDistribution: uint256[NUM_WORDS]
s_lotteryBalance: HashMap[uint256, uint256]
s_rewardsBalance: HashMap[address, uint256]
s_numberOfCombination: HashMap[uint256, HashMap[String[312], uint256]]
s_playerTickets: HashMap[uint256, HashMap[address, DynArray[uint256[NUM_WORDS], MAX_BUYING_TICKET]]]
s_playerTicketsRevealed: HashMap[uint256, HashMap[address, bool]]
s_winningTicket: HashMap[uint256, uint256[NUM_WORDS]]

event StartLottery:
    lotteryNumber: indexed(uint256)
    startTime: uint256

event EnterLottery:
    lotteryNumber: indexed(uint256)
    player: indexed(address)

event EmitTicket:
    lotteryNumber: indexed(uint256)
    player: indexed(address)
    ticket: uint256[NUM_WORDS]

event RequestLotteryWinningTicket:
    lotteryNumber: indexed(uint256)
    requestId: indexed(uint256)

event WinningTicketLotteryPicked:
    lotteryNumber: indexed(uint256)
    ticket: uint256[NUM_WORDS]

event RevealTicket:
    lotteryNumber: indexed(uint256)
    player: indexed(address)
    ticket: uint256[NUM_WORDS]
    nbMatching: uint256

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
    _interval: uint256,
    _prizeDistribution: uint256[NUM_WORDS]
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
    @param _prizeDistribution Array of prize distribution of each pot (the smallest first, total must be 100%)
    """
    prizeDistributionTotal: uint256 = 0
    for prizeDistribution in _prizeDistribution:
        prizeDistributionTotal = prizeDistributionTotal + prizeDistribution
    assert prizeDistributionTotal == 100, "Prize distribution not 100%"
    i_vrfCoordinator = VRFCoordinatorV2Interface(_vrfCoordinatorV2)
    i_subscriptionId = _subscriptionId
    i_gasLane = _gasLane
    i_callbackGasLimit = _callbackGasLimit
    i_ethUsdPriceFeed = AggregatorV3Interface(_ethUsdPriceFeed)
    i_usdTicketFee = _usdEntranceFee * (10 ** 18)
    i_interval = _interval
    self.s_randNonce = 0
    self.s_lotteryNumber = 1
    self.s_prizeDistribution = _prizeDistribution
    self.s_lotteryState = LotteryState.OPEN

@external
@payable
def buyTickets(_numberOfTickets: uint256):
    """
    @notice Allow user to buy tickets to enter the lottery by paying ticket fee
    @param _numberOfTickets The number of ticket the user want to buy
    @dev When the first player enter the lottery the duration start
    emit an event EnterLottery when player enter the lottery
    emit an event EmitTicket for each ticket the player buys
    emit an event StartLottery the lottery duration start
    """
    assert self.s_lotteryState == LotteryState.OPEN, "Lottery not open"
    assert len(self.s_playerTickets[self.s_lotteryNumber][msg.sender]) + _numberOfTickets <= MAX_BUYING_TICKET, "Too many tickets"
    assert msg.value >= self.getTicketFeeInternal() * _numberOfTickets, "Not enough funds"
    if not self.isPlayerAlreadyInLottery(msg.sender):
        self.s_players.append(msg.sender)
        log EnterLottery(self.s_lotteryNumber, msg.sender)
        if(len(self.s_players) == 1):
            self.s_startTimestamp = block.timestamp
            log StartLottery(self.s_lotteryNumber, self.s_startTimestamp)
    for ticketIndex in range(MAX_BUYING_TICKET):
        if ticketIndex >= _numberOfTickets:
            break
        ticket: uint256[NUM_WORDS] = [
            self.getRandomNumber(),
            self.getRandomNumber(),
            self.getRandomNumber(),
            self.getRandomNumber()
        ]
        self.s_playerTickets[self.s_lotteryNumber][msg.sender].append(ticket)
        self.setNumberOfCombinations(self.s_lotteryNumber, ticket)
        log EmitTicket(self.s_lotteryNumber, msg.sender, ticket)
    self.s_lotteryBalance[self.s_lotteryNumber] += msg.value

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
    Call Chainlink VRF to request a random winning ticket
    emit an event RequestLotteryWinningTicket when request winning ticket is called
    """
    upkeep_needed: bool = self.isLotteryMustEnd()
    assert upkeep_needed, "Upkeep not needed"
    self.s_lotteryState = LotteryState.DRAW_WINNING_TICKET
    requestId: uint256 = i_vrfCoordinator.requestRandomWords(i_gasLane, i_subscriptionId, REQUEST_CONFIRMATIONS, i_callbackGasLimit, NUM_WORDS)
    log RequestLotteryWinningTicket(self.s_lotteryNumber, requestId)

@internal
def fulfillRandomWords(_requestId: uint256, _randomWords: DynArray[uint256, MAX_ARRAY_SIZE]):
    """
    @notice Picked a random winning ticket and restart lottery
    @dev Call by the Chainlink VRF after requesting a random winning ticket
    emit an event WinningTicketLotteryPicked when random winning ticket has been picked
    """
    winningTicket: uint256[NUM_WORDS] = [
        _randomWords[0] % 10,
        _randomWords[1] % 10,
        _randomWords[2] % 10,
        _randomWords[3] % 10
    ]
    self.s_winningTicket[self.s_lotteryNumber] = winningTicket
    self.postponeLotteryBalance()
    self.s_players = []
    self.s_lotteryState = LotteryState.OPEN
    self.s_lotteryNumber += 1
    log WinningTicketLotteryPicked(self.s_lotteryNumber-1, winningTicket)

@external
def rawFulfillRandomWords(_requestId: uint256, _randomWords: DynArray[uint256, MAX_ARRAY_SIZE]):
    """
    @notice In solidity, this is the equivalent of inheriting the VRFConsumerBaseV2
    Vyper doesn't have inheritance, so we just add the function here
    """
    assert msg.sender == i_vrfCoordinator.address, "Only coordinator can fulfill!"
    self.fulfillRandomWords(_requestId, _randomWords)

@external
def revealWinningTickets(_lotteryNumber: uint256):
    """
    @notice Allow user to reveal if his tickets are winning tickets for a specific lottery
    @param _lotteryNumber The number of the lottery
    emit an event RevealTicket for each ticket revealed
    """
    assert _lotteryNumber >= 1 and _lotteryNumber < self.s_lotteryNumber, "Non existing lottery"
    assert not self.isPlayerTicketAlreadyRevealedInternal(msg.sender, _lotteryNumber), "Tickets already revealed"
    totalRewards: uint256 = 0
    winningTicket: uint256[NUM_WORDS] = self.s_winningTicket[_lotteryNumber]
    ticketList: DynArray[uint256[NUM_WORDS], MAX_BUYING_TICKET] = self.s_playerTickets[_lotteryNumber][msg.sender]
    for ticket in ticketList:
        nbMatching: uint256 = self.getNumberOfMatching(ticket, winningTicket)
        nbCombination: uint256 = self.getNumberOfCombinations(_lotteryNumber, nbMatching, ticket)
        totalRewards += self.getPrizeForMatching(_lotteryNumber, nbMatching, nbCombination)
        log RevealTicket(_lotteryNumber, msg.sender, ticket, nbMatching)
    self.s_rewardsBalance[msg.sender] += totalRewards
    self.s_playerTicketsRevealed[_lotteryNumber][msg.sender] = True

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
def setNumberOfCombinations(_lotteryNumber: uint256, _ticket: uint256[NUM_WORDS]):
    """
    @notice Set the combinations for a specific ticket
    @param _lotteryNumber The lottery number
    @param _ticket The ticket
    @dev This function aim to set how many times a combination appear on the same lottery
    The purpose is to calulate at the end between how many user the pot need to be shared
    """
    self.s_numberOfCombination[_lotteryNumber][uint2str(_ticket[0])] += 1
    self.s_numberOfCombination[_lotteryNumber][concat(uint2str(_ticket[0]),uint2str(_ticket[1]))] += 1
    self.s_numberOfCombination[_lotteryNumber][concat(uint2str(_ticket[0]),uint2str(_ticket[1]),uint2str(_ticket[2]))] += 1
    self.s_numberOfCombination[_lotteryNumber][concat(uint2str(_ticket[0]),uint2str(_ticket[1]),uint2str(_ticket[2]),uint2str(_ticket[3]))] += 1

@internal
def getRandomNumber() -> uint256:
    """
    @notice Return a random number between 0 and 9
    @return randomNumber Random number
    @dev It's not a secure method to pick random number but as it's just to assign a ticket we can tolerate it
    """
    self.s_randNonce += 1
    return convert(keccak256(concat(convert(block.timestamp, bytes32), convert(msg.sender, bytes32), convert(self.s_randNonce, bytes32))), uint256) % 10

@internal
def postponeLotteryBalance():
    """
    @notice Postpone the lottery pots which don't have any winners to the next lottery
    """
    for numberIndex in range(NUM_WORDS):
        nbMatching: uint256 = convert(numberIndex, uint256)
        numberOfCombination: uint256 = self.getNumberOfCombinations(self.s_lotteryNumber, nbMatching + 1, self.s_winningTicket[self.s_lotteryNumber])
        if numberOfCombination == 0:
            poolDistribution: uint256 = self.s_prizeDistribution[nbMatching]
            prize: uint256 = (self.s_lotteryBalance[self.s_lotteryNumber] * poolDistribution) / 100
            self.s_lotteryBalance[self.s_lotteryNumber + 1] += prize

@internal
@pure
def getNumberOfMatching(_ticket: uint256[NUM_WORDS], _winningTicket: uint256[NUM_WORDS]) -> uint256:
    """
    @notice Return the number of matching number between a ticket and a winning ticket
    @param _ticket The ticket to compare
    @param _winningTicket The winning ticket
    @return nbMatching The number of matching numbers
    """
    nbMatching: uint256 = 0
    for numberIndex in range(NUM_WORDS):
        if _ticket[numberIndex] != _winningTicket[numberIndex]:
            break
        nbMatching += 1
    return nbMatching

@internal
@view
def getNumberOfCombinations(_lotteryNumber: uint256, _nbMatching: uint256, _ticket: uint256[NUM_WORDS]) -> uint256:
    """
    @notice Get the number of combinations for a specific ticket and its number of matching numbers
    @param _lotteryNumber The lottery number
    @param _nbMatching The number of matching numbers
    @param _ticket The ticket
    @return numberOfCombination The number of combination
    """
    if _nbMatching == 1:
        return self.s_numberOfCombination[_lotteryNumber][uint2str(_ticket[0])]
    if _nbMatching == 2:
        return self.s_numberOfCombination[_lotteryNumber][concat(uint2str(_ticket[0]),uint2str(_ticket[1]))]
    if _nbMatching == 3:
        return self.s_numberOfCombination[_lotteryNumber][concat(uint2str(_ticket[0]),uint2str(_ticket[1]),uint2str(_ticket[2]))]
    if _nbMatching == 4:
        return self.s_numberOfCombination[_lotteryNumber][concat(uint2str(_ticket[0]),uint2str(_ticket[1]),uint2str(_ticket[2]),uint2str(_ticket[3]))]
    return 0

@internal
@view
def getPrizeForMatching(_lotteryNumber: uint256, _nbMatching: uint256, _nbCombination: uint256) -> uint256:
    """
    @notice Return the amount a user will get from the number of matching numbers and the number of combinations
    @param _lotteryNumber The lottery number
    @param _nbMatching The number of matching numbers
    @param _nbCombination The number of combination
    @return prize The prize the user will get
    """
    prize: uint256 = 0
    if _nbMatching == 0:
        return 0
    poolDistribution: uint256 = self.s_prizeDistribution[_nbMatching - 1]
    prize = (self.s_lotteryBalance[_lotteryNumber] * poolDistribution) / 100
    return prize / _nbCombination

@internal
@view
def isPlayerAlreadyInLottery(_user: address) -> bool:
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
def isPlayerTicketAlreadyRevealedInternal(_user: address, _lotteryNumber: uint256) -> bool:
    """
    @notice Check if the user already revealed his tickets for the given lottery
    @param _user address of the user
    @param _lotteryNumber The number of the lottery
    @return isAlreadyRevealed true if already revealed, false ether
    """
    return self.s_playerTicketsRevealed[_lotteryNumber][_user]

@external
@view
def isPlayerTicketAlreadyRevealed(_user: address, _lotteryNumber: uint256) -> bool:
    """
    @notice Check if the user already revealed his tickets for the given lottery
    @param _user address of the user
    @param _lotteryNumber The number of the lottery
    @return isAlreadyRevealed true if already revealed, false ether
    @dev For external call
    """
    return self.isPlayerTicketAlreadyRevealedInternal(_user, _lotteryNumber)

@internal
@view
def getTicketFeeInternal() -> uint256:
    """
    @notice Get ticket fee to participate to the lottery
    @return ticketFee Ticket fee in ETH
    @dev Implements Chainlink price feed
    """
    a: uint80 = 0
    price: int256 = 0
    b: uint256 = 0
    c: uint256 = 0
    d: uint80 = 0
    (a,price,b,c,d) = i_ethUsdPriceFeed.latestRoundData()
    adjustedPrice: uint256 = convert(price, uint256) * 10 ** 10
    return (i_usdTicketFee * 10 ** 18) / adjustedPrice

@external
@view
def getTicketFee() -> uint256:
    """
    @notice Get ticket fee to participate to the lottery
    @return ticketFee Ticket fee in ETH
    @dev Implements Chainlink price feed
    For external call
    """
    return self.getTicketFeeInternal()

@external
@view
def getUsdTicketFee() -> uint256:
    """
    @notice Get ticket fee in dollars to participate to the lottery
    @return usdTicketFee Ticket fee in dollars
    """
    return i_usdTicketFee

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
def getPrizeDistribution() -> uint256[NUM_WORDS]:
    """
    @notice Get the prize distribution of the lottery
    @return prizeDistribution Prize distribution of the lottery
    """
    return self.s_prizeDistribution

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
def getPlayerTicket(_user: address, _index: uint256) -> uint256[NUM_WORDS]:
    """
    @notice Get a specific ticket for the player on the lottery
    @param _user user address
    @param _index Index of ticket
    @return ticket The player ticket
    """
    return self.s_playerTickets[self.s_lotteryNumber][_user][_index]

@external
@view
def getNumberOfTicketsByPlayer(_user: address) -> uint256:
    """
    @notice Get the number of ticket a player own in the lottery
    @return numTicketPlayer Number of tickets for the player
    """
    return len(self.s_playerTickets[self.s_lotteryNumber][_user])

@external
@view
def getNumberOfCombination(_combination: String[312]) -> uint256:
    """
    @notice Get the number of time a combination appear
    @return numCombination Number of combination
    """
    return self.s_numberOfCombination[self.s_lotteryNumber][_combination]

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
def getWinningTicket(_lotteryNumber: uint256) -> uint256[NUM_WORDS]:
    """
    @notice Get the winning ticket of a specific lottery
    @param _lotteryNumber The number of the lottery
    @return winningTicket Lottery winning ticket
    """
    return self.s_winningTicket[_lotteryNumber]

@external
@view
def getUserRewardsBalance(_user: address) -> uint256:
    """
    @notice Get the user pending rewards of his winning lotteries
    @param _user address of the user
    @return rewardsBalance Rewards balance
    """
    return self.s_rewardsBalance[_user]
