## DYDX Docs
Source: https://dydxprotocol.github.io/v3-teacher/#portfolio-margining

## Portfolio Margining
There is no distinction between realized and unrealized PnL for the purposes of margin calculations. Gains from one position will offset losses from another position within the same account, regardless of whether the profitable position is closed.

### Margin Calculation
The margin requirement for a single position is calculated as follows:

* Initial Margin Requirement = abs(S × P × I)

* Maintenance Margin Requirement = abs(S × P × M)

Where:

* **S** is the size of the position (positive if long, negative if short)
* **P** is the oracle price for the market
* **I** is the initial margin fraction for the market 
* **M** is the maintenance margin fraction for the market

The margin requirement for the account as a whole is the sum of the margin requirement over each market i in which the account holds a position:

* Total Initial Margin Requirement = Σ abs(Si × Pi × Ii)
* Total Maintenance Margin Requirement = Σ abs(Si × Pi × Mi)

The total margin requirement is compared against the total value of the account, which incorporates the quote asset (USDC) balance of the account as well as the value of the positions held by the account:

* Total Account Value = Q + Σ (Si × Pi)
* The Total Account Value is also referred to as equity.

Where:

**Q** is the account's USDC balance (note that **Q** may be negative). In the API, this is called quoteBalance. Every time a transfer, deposit or withdrawal occurs for an account, the balance changes. Also, when a position is modified for an account, the quoteBalance changes. Also funding payments and liquidations will change an account's quoteBalance.
**S** and **P** are as defined above (note that **S** may be negative)
An account cannot open new positions or increase the size of existing positions if it would lead the total account value of the account to drop below the total initial margin requirement. If the total account value ever falls below the total maintenance margin requirement, the account may be liquidated.

Free collateral is calculated as:

* Free collateral = Total Account Value - Total Initial Margin Requirement
* Equity and free collateral can be tracked over time using the latest oracle price (obtained from the markets websocket).
-------
## Liquidations
Accounts whose total value falls below the maintenance margin requirement (described above) may have their positions automatically closed by the liquidation engine. Positions are closed at the close price described below. Profits or losses from liquidations are taken on by the insurance fund.

### Close Price for Liquidations

The close price for a position being liquidated is calculated as follows, depending whether it is a short or long position:

* Close Price (Short) = P × (1 + (M × V / W))
* Close Price (Long) = P × (1 − (M × V / W))

Where:

* **P** is the oracle price for the market
* **M** is the maintenance margin fraction for the market
* **V** is the total account value, as defined above
* **W** is the total maintenance margin requirement, as defined above

This formula is chosen such that the ratio **V / W** is unchanged as individual positions are liquidated.