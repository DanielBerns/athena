import datetime

def generate_dates_with_criteria(start_date_str, end_date_str):
  """
  Generates a list of dates between start_date and end_date (inclusive)
  that meet either of the following criteria:
  1. The date is the 1st or 15th of the month.
  2. The date is a Wednesday.

  Args:
    start_date_str (str): The start date in 'YYYY-MM-DD' format.
    end_date_str (str): The end date in 'YYYY-MM-DD' format.

  Returns:
    list: A list of datetime.date objects meeting the criteria, sorted chronologically.
          Returns an empty list if start_date > end_date.
    str: An error message if date parsing fails.
  """
  try:
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
  except ValueError:
    return "Invalid date format. Please use 'YYYY-MM-DD'."

  if start_date > end_date:
    return [] # Return empty list if range is invalid

  result_dates = []
  current_date = start_date
  one_day = datetime.timedelta(days=1)

  while current_date <= end_date:
    # Criterion 1: Check if the day is 1st or 15th
    is_first_or_fifteenth = current_date.day == 1 or current_date.day == 15

    # Criterion 2: Check if it's a Wednesday
    # weekday() returns 0 for Monday, 1 for Tuesday, ..., 6 for Sunday
    is_wednesday = current_date.weekday() == 2 # Wednesday corresponds to 2

    # Add the date if either criterion is met
    if is_first_or_fifteenth or is_wednesday:
      result_dates.append(current_date)

    # Move to the next day
    current_date += one_day

  # The loop naturally generates sorted dates, but ensures uniqueness implicitly.
  # If overlap could occur and needs removal (e.g., Wed, 1st or Wed, 15th),
  # converting to a set and back to a sorted list would handle it,
  # but appending only once per date already achieves this.
  # Example: return sorted(list(set(result_dates))) # If duplicates were possible

  return result_dates

# --- How to use it ---

def main() -> None:
    # 1. Define your start and end dates (use 'YYYY-MM-DD' format)
    start = '2020-01-01'
    end = '2026-12-31'

    # 2. Call the function
    list_of_dates = generate_dates_with_criteria(start, end)

    # 3. Print the results
    if isinstance(list_of_dates, str): # Check if an error message was returned
      print(list_of_dates)
    else:
      print(f"Dates between {start} and {end} that are 1st/15th OR a Wednesday:")
      if not list_of_dates:
        print("No dates found matching the criteria in this range.")
      else:
        # You can format the output dates if needed
        for date_obj in list_of_dates:
          # Print with date and day name for clarity
          print(date_obj.strftime('%Y-%m-%d (%A)'))

    # # --- Example with today's date context ---
    # # Using the current date provided (April 16, 2025) for a short example
    # today = datetime.date(2025, 4, 16)
    # start_example = (today - datetime.timedelta(days=20)).strftime('%Y-%m-%d') # Approx March 27th
    # end_example = (today + datetime.timedelta(days=20)).strftime('%Y-%m-%d')   # Approx May 6th
    #
    # print("\n--- Example around April 16, 2025 ---")
    # example_dates = generate_dates_with_criteria(start_example, end_example)
    # if isinstance(example_dates, str):
    #     print(example_dates)
    # else:
    #     print(f"Dates between {start_example} and {end_example} matching criteria:")
    #     for date_obj in example_dates:
    #         print(date_obj.strftime('%Y-%m-%d (%A)'))
    #

if __name__ == "__main__":
    main()

