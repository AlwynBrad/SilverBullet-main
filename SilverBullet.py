import pandas as pd
from datetime import datetime, timedelta

# Read the CSV file containing trading data
df = pd.read_csv("C:\\\Users\\alwyn\\Desktop\\SilverBullet-main\\usatechidxusd-m5-bid-2024-04-22-2024-04-23.csv")
# Convert Unix epoch timestamps to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Convert timestamps from UTC to EST
df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)

# Function to identify key highs and lows for sessions
def identify_key_highs_lows(df, date):
    # Calculate the date of the previous day
    previous_day = date - pd.Timedelta(days=1)
    
    # Filter data for the Asia session on the previous day
    asia_session = df[(df['timestamp'].dt.date == previous_day) & (df['timestamp'].dt.hour >= 18)].copy()
    
    # Check if there are any rows for the previous day's Asia session
    if not asia_session.empty:
        asia_high = asia_session['high'].max()
        asia_low = asia_session['low'].min()
    else:
        asia_high = None
        asia_low = None
    
    # Filter data for the London session
    london_session = df[(df['timestamp'].dt.date == date) & (df['timestamp'].dt.hour >= 0) & (df['timestamp'].dt.hour < 6)].copy()
    
    # Filter data for the Pre-New York session
    pre_new_york_session = df[(df['timestamp'].dt.date == date) & (df['timestamp'].dt.hour >= 6) & (df['timestamp'].dt.hour < 7.5)].copy()
    
    # Calculate highest high and lowest low for London and Pre-New York sessions
    london_high = london_session['high'].max()
    london_low = london_session['low'].min()
    pre_new_york_high = pre_new_york_session['high'].max()
    pre_new_york_low = pre_new_york_session['low'].min()

    return asia_high, asia_low, london_high, london_low, pre_new_york_high, pre_new_york_low

# Function to check for breakouts
def check_breakout(df, date, asia_high, london_high, pre_new_york_high, asia_low, london_low, pre_new_york_low):
    # Set the start time to midnight of the current day
    start_time = datetime.combine(date, datetime.min.time())  # Midnight of the current day
    end_time = start_time + timedelta(hours=9, minutes=30)  # 9:30 AM of the current day
    df_midnight_to_9_30am = df[(df['timestamp'] >= start_time) & (df['timestamp'] < end_time)].copy()
    
    # Get the maximum high and minimum low within the specified period
    max_high_midnight_to_9_30am = df_midnight_to_9_30am['high'].max()
    min_low_midnight_to_9_30am = df_midnight_to_9_30am['low'].min()
    
    # Ensure no nonetype
    if (asia_high is not None and 
        asia_low is not None and 
        london_high is not None and 
        london_low is not None and 
        pre_new_york_high is not None and 
        pre_new_york_low is not None):

        # Check for breakout in high prices
        if max_high_midnight_to_9_30am > pre_new_york_high or max_high_midnight_to_9_30am > london_high or max_high_midnight_to_9_30am > asia_high:
            return True, max_high_midnight_to_9_30am, 'high'
        # Check for breakout in low prices
        elif min_low_midnight_to_9_30am < pre_new_york_low or min_low_midnight_to_9_30am < london_low or min_low_midnight_to_9_30am < asia_low:
            return True, min_low_midnight_to_9_30am, 'low'
        else:
            return False, None, None
        
    else:
        return False, None, None

# Function to find fair value gaps
def find_fair_value_gaps(df, start_time, end_time):
    df = df[(df['timestamp'].dt.hour >= start_time) & (df['timestamp'].dt.hour < end_time)]
    fair_value_gaps = []

    for i in range(len(df) - 2):
        current_candle = df.iloc[i]
        next_next_candle = df.iloc[i + 2]

        if current_candle['high'] < next_next_candle['low']:
            fair_value_gaps.append((current_candle['timestamp'], next_next_candle['timestamp'], 'bullish'))
        
        elif current_candle['low'] > next_next_candle['high']:
            fair_value_gaps.append((current_candle['timestamp'], next_next_candle['timestamp'], 'bearish'))

    return fair_value_gaps

# Function to determine the direction of fair value gaps
def determine_gap_direction(df, fair_value_gaps):
    gap_directions = []

    for gap in fair_value_gaps:
        start_time = gap[0]
        end_time = gap[1]
        gap_df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]
        if gap_df.iloc[1]['open'] < gap_df.iloc[1]['close']:
            gap_directions.append('bullish')
        else:
            gap_directions.append('bearish')

    return gap_directions

# Function to determine position to enter
def enter_position(direction, breakout_type):
    if direction == 'bearish' and breakout_type == 'high':
        return 'short'
    elif direction == 'bullish' and breakout_type == 'low':
        return 'long'
    else:
        return None

# Function to calculate stop-loss level
def calculate_stop_loss(df, entry_price, direction, gap):
    gap_end_time = gap[1]
    gap_row = df[df['timestamp'] == gap_end_time].iloc[0]
    if direction == 'bearish':
        stop_loss = gap_row['high']
    elif direction == 'bullish':
        stop_loss = gap_row['low']
    return stop_loss

# Function to calculate target level
def calculate_target(entry_price, stop_loss, direction):
    risk_reward_ratio = 2
    if direction == 'bullish':
        target = entry_price + (entry_price - stop_loss) * risk_reward_ratio
    elif direction == 'bearish':
        target = entry_price - (stop_loss - entry_price) * risk_reward_ratio
    return target

# Portfolio class to manage balance and equity curve
class Portfolio:
    def __init__(self, initial_balance=100000):
        self.balance = initial_balance
        self.equity_curve = []

    def update_balance(self, amount):
        self.balance += amount

# Initialize portfolio
portfolio = Portfolio()

# Function to calculate entry price
def calculate_entry_price(df, gap_direction, gap):
    gap_end_time = gap[1]
    gap_row = df[df['timestamp'] == gap_end_time].iloc[0]
    if gap_direction == 'bullish':
        return gap_row['low']  # Entry price for bullish trade is the low of the third candle
    elif gap_direction == 'bearish':
        return gap_row['high']  # Entry price for bearish trade is the high of the third candle

# Function to execute strategy
def execute_strategy(df, portfolio):
    unique_dates = df['timestamp'].dt.date.unique()
    
    for date in unique_dates:
        asia_high, asia_low, london_high, london_low, pre_new_york_high, pre_new_york_low = identify_key_highs_lows(df, date)
        breakout, entry_price, breakout_type = check_breakout(df, date, asia_high, london_high, pre_new_york_high, asia_low, london_low, pre_new_york_low)
        
        if breakout:
            fair_value_gaps = find_fair_value_gaps(df, 10, 11) + find_fair_value_gaps(df, 14, 15)
            if fair_value_gaps:
                for i, gap in enumerate(fair_value_gaps):
                    if i == 0:  # Only consider the first fair value gap after 10:00 AM EST and the first fair value gap after 2:00 PM EST
                        gap_direction = determine_gap_direction(df, [gap])[0]
                        position = enter_position(gap_direction, breakout_type)
                        if position:
                            entry_price = calculate_entry_price(df, gap_direction, gap)
                            stop_loss = calculate_stop_loss(df, entry_price, gap_direction, gap)
                            target = calculate_target(entry_price, stop_loss, gap_direction)
                            print(f"Enter {position} position at price {entry_price} based on {gap_direction} fair value gap and {breakout_type} breakout.")
                            print(f"Stop-loss: {stop_loss}, Target: {target}")

                            # Update trade status based on candle movements
                            for index, candle in df.iterrows():
                                if candle['timestamp'].hour < 23:  # Iterate until 23:00 EST
                                    if position == 'long':
                                        if candle['low'] < stop_loss:
                                            print("Trade marked as loss.")
                                            portfolio.update_balance(-0.005 * portfolio.balance)  # Subtract 0.5% from initial balance for loss
                                            break
                                        elif candle['high'] > target:
                                            print("Trade marked as profit.")
                                            portfolio.update_balance(0.01 * portfolio.balance)  # Add 1% to initial balance for profit
                                            break
                                    elif position == 'short':
                                        if candle['high'] > stop_loss:
                                            print("Trade marked as loss.")
                                            portfolio.update_balance(-0.005 * portfolio.balance)  # Subtract 0.5% from initial balance for loss
                                            break
                                        elif candle['low'] < target:
                                            print("Trade marked as profit.")
                                            portfolio.update_balance(0.01 * portfolio.balance)  # Add 1% to initial balance for profit
                                            break
                                else:
                                    print("No trade status update after entering into a position.")
                                    break
                        else:
                            print("No position to enter.")
                        break  # Exit loop after processing the first fair value gap
                else:
                    print("No fair value gaps found after 10:00 AM EST and 2:00 PM EST.")
            else:
                print("No fair value gaps found.")
        else:
            print("No breakout detected.")

# Print portfolio balance
def print_portfolio_balance(portfolio):
    print(f"Portfolio Balance: {portfolio.balance}")

# Execute strategy for each trading day
execute_strategy(df, portfolio)

# Print final portfolio balance
print_portfolio_balance(portfolio)
