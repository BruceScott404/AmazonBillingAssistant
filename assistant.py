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

    sales_tax = str(row['product sales tax'])
    sales = str(row['product sales'])
    sales_tax = float(sales_tax.replace(',',''))
    sales = float(sales.replace(',',''))
    tax = float(sales_tax / sales)
    float_tax = tax*100
    tax = int(round(tax * 100))

    if tax != bracket:
        print("Tax wrong: " + str(float_tax) + ":" + str(bracket) + "\n" + str(row))

    if bracket == 13:
        bracket_13.append(row)
    elif bracket == 15:
        bracket_15.append(row)
    elif bracket == 5:
        with open ('test.txt', 'a') as f:
            f.write(row['order id'])
            f.write('\n')
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
    elif bracket == 5:
        refund_bracket_5.append(row)




def aggregate_data(bracket_13_df, filename):

    # Define the columns to aggregate
    columns_to_aggregate = [
        'quantity', 'product sales', 'shipping credits', 'selling fees','fba fees', 'other transaction fees', 'other', 'Regulatory fee', 'total'
    ]

    amazon_columns = [
        'selling fees','fba fees', 'other transaction fees', 'other', 'Regulatory fee'
    ]

    # Group by 'sku' and sum the specified columns
    bracket_13_df[columns_to_aggregate] = bracket_13_df[columns_to_aggregate].replace(',', '', regex=True)
    bracket_13_df[columns_to_aggregate] = bracket_13_df[columns_to_aggregate].apply(pd.to_numeric, errors='coerce')
    aggregated_13 = bracket_13_df.groupby('sku', as_index=False)[columns_to_aggregate].sum()
    aggregated_13['Total of Amazon Fees'] = aggregated_13[amazon_columns].sum(axis=1)
    fees = aggregated_13['Total of Amazon Fees']
    aggregated_13 = aggregated_13.drop(columns=['Total of Amazon Fees'])
    aggregated_13.insert(9, 'Total of Amazon Fees', fees)
    aggregated_13 = aggregated_13.drop(columns=amazon_columns)

    # Calculate the total for each aggregated entry
    # aggregated_13['total'] = (
    #     aggregated_13['total']
    # )

    # Save the aggregated DataFrame to a CSV file
    aggregated_13.to_csv(filename, index=False)
    return aggregated_13


def format_data(frames, filename):
    columns = [
        'sku', 'quantity', 'product sales', 'shipping credits', 'Total of Amazon Fees', 'total'
    ]
    output_frame = pd.DataFrame(columns=columns)
    overall_totals = pd.DataFrame(columns=columns)

    run = 0
    for frame in frames:
        totals = pd.DataFrame(frame[columns].sum()).transpose()
        if run == 0:
            totals['sku'] = 'FINDEME 0.05'
        elif run == 1:
            totals['sku'] = 'FINDME 0.13'
        else:
            totals['sku'] = 'FINDME 0.15'
        run += 1
        output_frame = pd.concat([output_frame, totals])
        output_frame = pd.concat([output_frame, frame])
        overall_totals = pd.concat([overall_totals, totals])
    
    overall_totals = pd.DataFrame(overall_totals[columns].sum()).transpose()
    overall_totals['sku'] = 'TOTALS: '
    output_frame = pd.concat([output_frame, overall_totals])

    output_frame.to_csv(filename, index=False)


# Convert bracket_13 to a DataFrame if needed
bracket_13_df = pd.DataFrame(bracket_13)
bracket_15_df = pd.DataFrame(bracket_15)
bracket_5_df = pd.DataFrame(bracket_5)

refund_bracket_13_df = pd.DataFrame(refund_bracket_13)
refund_bracket_15_df = pd.DataFrame(refund_bracket_15)
refund_bracket_5_df = pd.DataFrame(refund_bracket_5)

sum = 0
for index, row in bracket_5_df.iterrows():
    if ',' in row['total']:
        fl = row['total'].replace(',','')
        sum += float(fl)

return_13 = aggregate_data(refund_bracket_13_df, "output/aggregated_refunds_13.csv")
return_15 = aggregate_data(refund_bracket_15_df, "output/aggregated_refunds_15.csv")
return_5 = aggregate_data(refund_bracket_5_df, "output/aggregated_refunds_5.csv")
aggregated_13 = aggregate_data(bracket_13_df, "output/aggregated_sales_13.csv")
aggregated_15 = aggregate_data(bracket_15_df, "output/aggregated_sales_15.csv")
aggregated_5 = aggregate_data(bracket_5_df, "output/aggregated_sales_5.csv")

format_data([aggregated_5, aggregated_13, aggregated_15], "orders.csv")
format_data([return_5, return_13, return_15], "returns.csv")
print("Calculations Completed...")