import pandas as pd
import unidecode

tax_rates = {}

with open("taxrates.txt", "r") as f:
    for line in f:
        splitLine = line.split(":")
        tax_rates[splitLine[0]] = int(splitLine[1])

# Load the CSV file
data = pd.read_csv('input/input.csv', header=0)

# Filter rows by 'Order'
orders = data[data['type'] == 'Order']

# Filter rows by 'Refund'
refunds = data[data['type'] == 'Refund']

bracket_5 = []
bracket_13 = []
bracket_15 = []

refund_bracket_5 = []
refund_bracket_13 = []
refund_bracket_15 = []


for index, row in orders.iterrows():
    bracket = 0
    try:
        bracket = tax_rates[unidecode.unidecode(row['order state']).lower()]
    except:
        try:
            bracket = tax_rates[unidecode.unidecode(row['order city']).lower()]
        except:
            print("ERROR: Province: ", row['order state'], " City: ", row['order city'], " not found")

    if bracket == 13:
        bracket_13.append(row)
    elif bracket == 15:
        bracket_15.append(row)
    else:
        bracket_5.append(row)

for index, row in refunds.iterrows():
    bracket = 0
    try:
        bracket = tax_rates[unidecode.unidecode(row['order state']).lower()]
    except:
        try:
            bracket = tax_rates[unidecode.unidecode(row['order city']).lower()]
        except:
            print("ERROR: Province: ", row['order state'], " City: ", row['order city'], " not found")
    if bracket == 13:
        refund_bracket_13.append(row)
    elif bracket == 15:
        refund_bracket_15.append(row)
    else:
        refund_bracket_5.append(row)


# Convert bracket_13 to a DataFrame if needed
bracket_13_df = pd.DataFrame(bracket_13)
bracket_15_df = pd.DataFrame(bracket_15)
bracket_5_df = pd.DataFrame(bracket_5)

def aggregate_data(data, filename):
    bracket_13_df = pd.DataFrame(data)

    # Define the columns to aggregate
    columns_to_aggregate = [
        'quantity', 'product sales', 'shipping credits', 'selling fees','fba fees', 'other transaction fees', 'other', 'total'
    ]

    # Group by 'sku' and sum the specified columns
    bracket_13_df[columns_to_aggregate] = bracket_13_df[columns_to_aggregate].apply(pd.to_numeric, errors='coerce')
    aggregated_13 = bracket_13_df.groupby('sku', as_index=False)[columns_to_aggregate].sum()

    # Calculate the total for each aggregated entry
    aggregated_13['total'] = (
        aggregated_13['total']
    )

    # Save the aggregated DataFrame to a CSV file
    aggregated_13.to_csv(filename, index=False)

aggregate_data(refund_bracket_13, "output/aggregated_refunds_13.csv")
aggregate_data(refund_bracket_15, "output/aggregated_refunds_15.csv")
aggregate_data(refund_bracket_5, "output/aggregated_refunds_5.csv")
aggregate_data(bracket_13, "output/aggregated_sales_13.csv")
aggregate_data(bracket_15, "output/aggregated_sales_15.csv")
aggregate_data(bracket_5, "output/aggregated_sales_5.csv")

print("Calculations Completed...")