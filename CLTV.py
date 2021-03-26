import pandas as pd
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("D:/MVK/week3/Dosyalar/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")

df = df_.copy()

##################################################
#  1. Calculate Average Order Value
##################################################

# CLTV = (Customer_Value / Churn_Rate) x Profit_margin.
# Customer_Value = Average_Order_Value * Purchase_Frequency
# Average_Order_Value = Total_Revenue / Total_Number_of_Orders
# Purchase_Frequency =  Total_Number_of_Orders / Total_Number_of_Customers
# Churn_Rate = 1 - Repeat_Rate
# Profit_margin
# Repeat Rate = Number of customer who at least 2 times shopping / Total customers number

def prep(dataframe):
    """
    We removed Invoices which 'C' containing. Because they meaning refund. So it could  affect incorrectly.
    If number of quantity is less than zero, it have been wrong enrollment so we removed them.
    We calculated Total Price for each item in a Invoice
    :param dataframe:
    :return:
    """
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    dataframe.dropna(inplace=True)
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    return dataframe


df = prep(df)

my_cltv = df.groupby("Customer ID").agg({
                            "Invoice": lambda y:len(y),"Quantity":lambda x: sum(x),
                            "TotalPrice": lambda v: sum(v)})

my_cltv.columns = ['total_transaction', 'total_unit', 'total_price']
print(my_cltv.head(),"\n")




# Purchase_Frequency =  Total_Number_of_Orders / Total_Number_of_Customers
# In here we made scaling.
# For each customer we divided Total number of ORDER to Total number of  CUSTOMERS.
total_customer_number = len(my_cltv)
my_cltv["purchase_freq"] = my_cltv['total_transaction'] / total_customer_number

print(my_cltv.head(),"\n")



# Average_Order_Value = Total_Revenue / Total_Number_of_Orders
# Purchase_Frequency =  Total_Number_of_Orders / Total_Number_of_Customers
# Customer_Value = Average_Order_Value * Purchase_Frequency
my_cltv["Average_order_value"] = my_cltv["total_price"] / my_cltv["total_transaction"]
my_cltv["Customer_value"] =  my_cltv["Average_order_value"] * my_cltv["purchase_freq"]



##################################################
#  Calculate Repeat Rate and Churn Rate
##################################################
# Churn_Rate = 1 - Repeat_Rate
def Churn_Rate(dataframe,transaction="total_transaction"):
    global total_customer_number
    dataframe = dataframe[dataframe[transaction]>1]
    number_transaction = len(dataframe)
    repeat_rate = number_transaction / total_customer_number
    churn_rate = 1 - repeat_rate
    return churn_rate

churn_rate = Churn_Rate(my_cltv)
print(churn_rate)


##################################################
# Calculate Profit Margin
##################################################
"We assumed that profit margin was %5"
my_cltv['profit_margin'] = my_cltv['total_price'] * 0.05


##################################################
# 5. Calculate Customer Lifetime Value
##################################################
# CLTV = (Customer_Value / Churn_Rate) x Profit_margin.

my_cltv["CV"]  = my_cltv["Customer_value"]  / churn_rate
my_cltv["CLTV"] = my_cltv["CV"] * my_cltv["profit_margin"]

print(my_cltv.head(10))


##################################################
# Comment Section
##################################################
from sklearn.preprocessing import MinMaxScaler

# we made scaling CLTV's values between 1-100 (It could be different like as 0-10 etc...)
scaler = MinMaxScaler(feature_range=(1,100))
scaler.fit(my_cltv[["CLTV"]])
my_cltv["CLTV_SCALE"] = scaler.transform(my_cltv[["CLTV"]])


# Segmentation of CLTV_SCALE
my_cltv["segment"] = pd.qcut(my_cltv["CLTV_SCALE"],q=4,labels=["D","C","B","A"])


print(my_cltv.sort_values(by="CLTV",ascending=False).head(7))


def sonuc(df,sutunlar = df.columns):
    while True:
        if "segment" not in sutunlar:

            #return False
            print("segment sütununu mutlaka veriniz")
            break
        my_new_columns = [col for col in sutunlar if (df[col].dtype != "object") ]
    print( (my_cltv[my_new_columns].groupby("segment").agg(["mean","sum","count"])).T)

sonuc(my_cltv,["total_transaction","total_unit","total_price","purchase_freq","CLTV_SCALE","segment"])



