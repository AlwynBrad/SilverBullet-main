import pandas as pd
from datetime import datetime, timedelta

# Read the CSV file containing trading data
# df = pd.read_csv("/mnt/E620153F2015185F/Alwyn Repos/SilverBullet-main/download/usatechidxusd-m5-bid-2024-01-01-2024-04-30T18_30.csv")
df = pd.read_csv("C:/Users/alwyn/Desktop/SilverBullet-main/download/usatechidxusd-m5-bid-2024-01-01-2024-04-30T18_30.csv")

# Convert Unix epoch timestamps to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Convert timestamps from UTC to EST
df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)

# Function to identify key highs and lows for sessions
def identify_key_highs_lows(df, date):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the identify_key_highs_lows function%%%%%%%%%%%%%")
    # Calculate the date of the previous day
    previous_day = date - pd.Timedelta(days=1)
    print(f"Date: {date}, Previous Day: {previous_day}")
    
    # Filter data for the Asia session on the previous day
    asia_session = df[(df['timestamp'].dt.date == previous_day) & (df['timestamp'].dt.hour >= 18)].copy()
    print("Asia Session:")
    print(asia_session)
    
    # Check if there are any rows for the previous day's Asia session
    if not asia_session.empty:
        asia_high = asia_session['high'].max()
        print(f"Asia High: {asia_high}")
        asia_low = asia_session['low'].min()
        print(f"Asia Low: {asia_low}")
    else:
        asia_high = None
        asia_low = None
        print("No data available for the Asia session on the previous day.")
    
    # Filter data for the London session
    london_session = df[(df['timestamp'].dt.date == date) & (df['timestamp'].dt.hour >= 0) & (df['timestamp'].dt.hour < 6)].copy()
    print("London Session:")
    print(london_session)

    # Filter data for the Pre-New York session
    pre_new_york_session = df[(df['timestamp'].dt.date == date) & (df['timestamp'].dt.hour >= 6) & (df['timestamp'].dt.hour < 7.5)].copy()
    print("Pre-New York Session:")
    print(pre_new_york_session)
    
    # Calculate highest high and lowest low for London and Pre-New York sessions
    london_high = london_session['high'].max()
    print(f"London High: {london_high}")
    london_low = london_session['low'].min()
    print(f"London Low: {london_low}")
    pre_new_york_high = pre_new_york_session['high'].max()
    print(f"Pre-New York High: {pre_new_york_high}")
    pre_new_york_low = pre_new_york_session['low'].min()
    print(f"Pre-New York Low: {pre_new_york_low}")

    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the identify_key_highs_lows function%%%%%%%%%%%%%")

    return asia_high, asia_low, london_high, london_low, pre_new_york_high, pre_new_york_low

# Function to check for breakouts
def check_breakout(df, date, asia_high, london_high, pre_new_york_high, asia_low, london_low, pre_new_york_low):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the check_breakout function%%%%%%%%%%%%%")
    # Set the start time to midnight of the current day
    start_time = datetime.combine(date, datetime.min.time())  # Midnight of the current day
    print(f"Start Time: {start_time}")
    end_time = start_time + timedelta(hours=9, minutes=30)  # 9:30 AM of the current day
    print(f"End Time: {end_time}")
    df_midnight_to_9_30am = df[(df['timestamp'] >= start_time) & (df['timestamp'] < end_time)].copy()
    print("Data from Midnight to 9:30 AM:")
    print(df_midnight_to_9_30am)
    
    # Get the maximum high and minimum low within the specified period
    max_high_midnight_to_9_30am = df_midnight_to_9_30am['high'].max()
    print(f"Max High from Midnight to 9:30 AM: {max_high_midnight_to_9_30am}")
    min_low_midnight_to_9_30am = df_midnight_to_9_30am['low'].min()
    print(f"Min Low from Midnight to 9:30 AM: {min_low_midnight_to_9_30am}")
    
    # Ensure no nonetype
    if (asia_high is not None and 
        asia_low is not None and 
        london_high is not None and 
        london_low is not None and 
        pre_new_york_high is not None and 
        pre_new_york_low is not None):

        # Check for breakout in high prices
        if max_high_midnight_to_9_30am > pre_new_york_high or max_high_midnight_to_9_30am > london_high or max_high_midnight_to_9_30am > asia_high:
            print("the max_high_midnight_to_9_30am is greater than the pre_new_york_high or london_high or asia_high")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the check_breakout function%%%%%%%%%%%%%")
            return True, max_high_midnight_to_9_30am, 'high'
        # Check for breakout in low prices
        elif min_low_midnight_to_9_30am < pre_new_york_low or min_low_midnight_to_9_30am < london_low or min_low_midnight_to_9_30am < asia_low:
            print("the min_low_midnight_to_9_30am is less than the pre_new_york_low or london_low or asia_low")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the check_breakout function%%%%%%%%%%%%%")
            return True, min_low_midnight_to_9_30am, 'low'
        else:
            print("No breakout detected.")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the check_breakout function%%%%%%%%%%%%%")
            return False, None, None
        
    else:
        print("Key highs and lows not available.")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the check_breakout function%%%%%%%%%%%%%")
        return False, None, None

# Function to find fair value gaps
def find_fair_value_gaps(df, start_time, end_time):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the find_fair_value_gaps function%%%%%%%%%%%%%")
    df = df[(df['timestamp'].dt.hour >= start_time) & (df['timestamp'].dt.hour < end_time)]
    fair_value_gaps = []

    for i in range(len(df) - 2):
        current_candle = df.iloc[i]
        next_next_candle = df.iloc[i + 2]

        if current_candle['high'] < next_next_candle['low']:
            fair_value_gaps.append((current_candle['timestamp'], next_next_candle['timestamp'], 'bullish'))
        
        elif current_candle['low'] > next_next_candle['high']:
            fair_value_gaps.append((current_candle['timestamp'], next_next_candle['timestamp'], 'bearish'))

    print(f"Fair Value Gaps between {start_time}:00 and {end_time}:00:")
    # print(fair_value_gaps)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the find_fair_value_gaps function%%%%%%%%%%%%%")
    return fair_value_gaps

# Function to determine the direction of fair value gaps
def determine_gap_direction(df, fair_value_gaps):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the determine_gap_direction function%%%%%%%%%%%%%")
    gap_directions = []

    for gap in fair_value_gaps:
        start_time = gap[0]
        end_time = gap[1]
        gap_df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]
        if gap_df.iloc[1]['open'] < gap_df.iloc[1]['close']:
            gap_directions.append('bullish')
        else:
            gap_directions.append('bearish')

    print(f"Gap Directions:")
    print(gap_directions)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the determine_gap_direction function%%%%%%%%%%%%%")
    return gap_directions

# Function to determine position to enter
def enter_position(direction, breakout_type):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the enter_position function%%%%%%%%%%%%%")
    if direction == 'bearish' and breakout_type == 'high':
        print("we are returning short from enter_position function")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the enter_position function%%%%%%%%%%%%%")
        return 'short'
    elif direction == 'bullish' and breakout_type == 'low':
        print("we are returning long from enter_position function")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the enter_position function%%%%%%%%%%%%%")
        return 'long'
    else:
        print("No position to enter.")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the enter_position function%%%%%%%%%%%%%")
        return None

# Function to calculate stop-loss level
def calculate_stop_loss(df, entry_price, direction, gap):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the calculate_stop_loss function%%%%%%%%%%%%%")
    gap_end_time = gap[1]
    print(f"Gap End Time: {gap_end_time}")
    gap_row = df[df['timestamp'] == gap_end_time].iloc[0]
    print(f"Gap Row:")
    print(gap_row)
    if direction == 'bearish':
        print("we are inside the bearish direction")
        print("we are assigning the stop loss as the high of the gap row, which is: ", gap_row['high'])
        stop_loss = gap_row['high']
    elif direction == 'bullish':
        print("we are inside the bullish direction")
        print("we are assigning the stop loss as the low of the gap row, which is: ", gap_row['low'])
        stop_loss = gap_row['low']

    print(f"Stop-loss: {stop_loss}")
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the calculate_stop_loss function%%%%%%%%%%%%%")
    return stop_loss

# Function to calculate target level
def calculate_target(entry_price, stop_loss, direction):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the calculate_target function%%%%%%%%%%%%%")
    risk_reward_ratio = 2
    print(f"Entry Price: {entry_price}, Stop-loss: {stop_loss}, Direction: {direction}")
    print(f"Risk-Reward Ratio: {risk_reward_ratio}")
    if direction == 'bullish':
        print("we are inside the bullish direction")
        target = entry_price + (entry_price - stop_loss) * risk_reward_ratio
        print(f"Target: {target}")
    elif direction == 'bearish':
        print("we are inside the bearish direction")
        target = entry_price - (stop_loss - entry_price) * risk_reward_ratio
        print(f"Target: {target}")
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the calculate_target function%%%%%%%%%%%%%")
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
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are inside the calculate_entry_price function%%%%%%%%%%%%%")
    print(f"Gap Direction: {gap_direction}")
    print(f"Gap: {gap}")
    gap_end_time = gap[1]
    print(f"Gap End Time: {gap_end_time}")
    gap_row = df[df['timestamp'] == gap_end_time].iloc[0]
    print(f"Gap Row:")
    if gap_direction == 'bullish':
        print("we are inside the bullish direction")
        print("we are returning the low of the gap row as the entry price, which is: ", gap_row['low'])
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the calculate_entry_price function%%%%%%%%%%%%%")
        return gap_row['low']  # Entry price for bullish trade is the low of the third candle
    elif gap_direction == 'bearish':
        print("we are inside the bearish direction")
        print("we are returning the high of the gap row as the entry price, which is: ", gap_row['high'])
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%we are outside the calculate_entry_price function%%%%%%%%%%%%%")
        return gap_row['high']  # Entry price for bearish trade is the high of the third candle

# Function to execute strategy
def execute_strategy(df, portfolio):
    unique_dates = df['timestamp'].dt.date.unique()
    count = 0
    for date in unique_dates:

        count += 1
        if count <= 2:
            continue

        print("\n\n################################## new day start ##########################################\n")
        print(f"Date: {date}")
        asia_high, asia_low, london_high, london_low, pre_new_york_high, pre_new_york_low = identify_key_highs_lows(df, date)
        print(f"Asia High: {asia_high}, Asia Low: {asia_low}, London High: {london_high}, London Low: {london_low}, Pre-New York High: {pre_new_york_high}, Pre-New York Low: {pre_new_york_low}")
        breakout, entry_price, breakout_type = check_breakout(df, date, asia_high, london_high, pre_new_york_high, asia_low, london_low, pre_new_york_low)
        print(f"Breakout: {breakout}, Entry Price: {entry_price}, Breakout Type: {breakout_type}")
        
        if breakout:
            print("Breakout detected.")
            fair_value_gaps = find_fair_value_gaps(df, 10, 11) + find_fair_value_gaps(df, 14, 15)
            # print(f"Fair Value Gaps:")
            # print(fair_value_gaps)
            if fair_value_gaps:
                print("Fair value gaps found.")
                for i, gap in enumerate(fair_value_gaps):
                    print(f"Gap: {gap}")
                    print(f"i: {i}")
                    if i == 0:  # Only consider the first fair value gap after 10:00 AM EST and the first fair value gap after 2:00 PM EST
                        gap_direction = determine_gap_direction(df, [gap])[0]
                        print(f"Fair value gap detected: {gap}")
                        position = enter_position(gap_direction, breakout_type)
                        print(f"Position to enter: {position}")
                        if position:
                            entry_price = calculate_entry_price(df, gap_direction, gap)
                            print(f"Entry price: {entry_price}")
                            stop_loss = calculate_stop_loss(df, entry_price, gap_direction, gap)
                            print(f"Stop-loss: {stop_loss}")
                            target = calculate_target(entry_price, stop_loss, gap_direction)
                            print(f"Enter {position} position at price {entry_price} based on {gap_direction} fair value gap and {breakout_type} breakout.")
                            print(f"Stop-loss: {stop_loss}, Target: {target}")

                            # Update trade status based on candle movements
                            for index, candle in df.iterrows():
                                if candle['timestamp'].hour < 23:  # Iterate until 23:00 EST
                                    print(f"Timestamp: {candle['timestamp']}, High: {candle['high']}, Low: {candle['low']}")
                                    if position == 'long':
                                        print(f"Current balance: {portfolio.balance}")
                                        if candle['low'] < stop_loss:
                                            print("Trade marked as loss.")
                                            portfolio.update_balance(-0.005 * portfolio.balance)  # Subtract 0.5% from initial balance for loss
                                            print(f"Updated balance: {portfolio.balance}")
                                            break
                                        elif candle['high'] > target:
                                            print("Trade marked as profit.")
                                            portfolio.update_balance(0.01 * portfolio.balance)  # Add 1% to initial balance for profit
                                            print(f"Updated balance: {portfolio.balance}")
                                            break
                                    elif position == 'short':
                                        if candle['high'] > stop_loss:
                                            print("Trade marked as loss.")
                                            portfolio.update_balance(-0.005 * portfolio.balance)  # Subtract 0.5% from initial balance for loss
                                            print(f"Updated balance: {portfolio.balance}")
                                            break
                                        elif candle['low'] < target:
                                            print("Trade marked as profit.")
                                            portfolio.update_balance(0.01 * portfolio.balance)  # Add 1% to initial balance for profit
                                            print(f"Updated balance: {portfolio.balance}")
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
