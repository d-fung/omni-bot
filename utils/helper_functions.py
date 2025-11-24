def decimal_to_american(decimal_odds):
    if decimal_odds >= 2:
        # Positive American odds
        american_odds = (decimal_odds - 1) * 100
        return f"+{int(american_odds)}"
    else:
        # Negative American odds
        american_odds = -100 / (decimal_odds - 1)
        return f"{int(american_odds)}"

def format_with_decimal(value):
    # Format with at least one decimal place
    return f"{value:.1f}"

def format_handicap(value):
    # Add "+" for positive values and leave negative values as is
    if value > 0:
        return f"+{format_with_decimal(value)}"
    else:
        return f"{format_with_decimal(value)}"

def generate_response_list(outputs):
    max_length = 2000
    response_list = []
    response = ''
    for output in outputs:
        
        if (len(response) + len(output)) > max_length:
            if response:
                response_list.append(response)
            response = output
        else:
            response += output
    
    if response:
        response_list.append(response)

    return response_list

        
