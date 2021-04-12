import json
import numpy as np
import pandas as pd
import datetime

from truck_lib import get_data

#dt = datetime.date(2018,12,12).isocalendar()[1]

# 1) TRUCK TYPE
truck_type = get_data('trucktype.json')

f = open('trucktype.json', 'r')
data = json.load(f)
f.close()
trucktype_df = pd.DataFrame(data)

# 2) TRUCK FLEET
f = open('truckfleet.json', 'r')
data = json.load(f)
f.close()
truckfleet_df = pd.DataFrame(data)

# 3) TRUCK COMPANY
f = open('truckcompany.json', 'r')
data = json.load(f)
f.close()
truckcompany_df = pd.DataFrame(data)

# 4) PACKAGING
f = open('packaging.json', 'r')
data = json.load(f)
f.close()
packaging_df = pd.DataFrame(data)

# 5) PRODUCTS
f = open('products.json', 'r')
data = json.load(f)
f.close()
products_df = pd.DataFrame(data)

# 6) DESTINATION LOCATION CLUSTER
f = open('destcluster.json', 'r')
data = json.load(f)
f.close()
destcluster_df = pd.DataFrame(data)

# 7) DESTINATION LOCATION CLUSTER
f = open('supploc.json', 'r')
data = json.load(f)
f.close()
supploc_df = pd.DataFrame(data)

# 8) ORDERS
f = open('orders.json', 'r')
data = json.load(f)
f.close()
orders_df = pd.DataFrame(data)

# MERGING
df_ord_product2 = orders_df.merge(
                                products_df,
                                on='SKU Code',
                                how='left')

df_ord_product_dest3 = df_ord_product2.merge(
                                        destcluster_df,
                                        on='Dest Code',
                                        how='left')
# df_ord_product_dest3['Destination Zip Code'] = df_ord_product_dest3['Destination Zip Code'].astype('str')
# df_ord_product_dest3['Destination Zip Code'].dtype


df_ord_product_dest_supp4 = df_ord_product_dest3.merge(
                                                    supploc_df,
                                                    on='Supplier',
                                                    how='left')

df_ord_product_dest_supp_pack5 = df_ord_product_dest_supp4.merge(
                                                        packaging_df,
                                                        on='Packaging Code',
                                                        how='left')

df_ord_product_dest_supp_pack5.drop([
                                    'Packaging Height (cm)',
                                    'Packaging Width (cm)' ,
                                    'Packaging Length (cm)'
                                    ],
                                axis='columns', inplace=True
                                )
#df_ord_product_dest_supp_pack5.dtypes
df_ord_product_dest_supp_pack5[['Destination Zip Code', 'Supplier Zip Code']] = \
    df_ord_product_dest_supp_pack5[['Destination Zip Code', 'Supplier Zip Code']].astype('str')

# CALCULATING TOTAL VOLUME (PER ORDER)
m_2_cm_cube = 1e6
df_ord_product_dest_supp_pack5['Total Volume Capacity (m3)'] = df_ord_product_dest_supp_pack5['Order Quantity (unit SKU)'] * \
                                                                df_ord_product_dest_supp_pack5['Packaging Capacity by Volume (cm3)'] / m_2_cm_cube
#df_ord_product_dest_supp_pack5['Total Volume Capacity (m3)'].sum()
df_ord_product_dest_supp_pack5.columns

# CALCULATING TOTAL WEIGHT (PER ORDER)
df_ord_product_dest_supp_pack5['Total Weight (kg)'] = df_ord_product_dest_supp_pack5['Order Quantity (unit SKU)'] * \
                                                                df_ord_product_dest_supp_pack5['SKU Weight (kg)']
#df_ord_product_dest_supp_pack5['Total Weight (kg)'].sum()

# df5_group_list = df_ord_product_dest_supp_pack5.groupby(['Requested Delivery Window', 'Destination Cluster','Supplier'])['Dest Code'].apply(','.join).reset_index()
# df5_group_list[['Requested Delivery Window', 'Destination Cluster','Supplier']].drop_duplicates()
s =df_ord_product_dest_supp_pack5.groupby(['Requested Delivery Window', 'Destination Cluster','Supplier'])['Dest Code'].apply(list)
set(s[0])

s1 = df5_group_list['Dest Code']
type(s1[0])
s1.index
df5_grouped1 = pd.concat([df5_grouped, df5_group_list['Dest Code']], axis=1)
df5_grouped=df5_grouped.drop('dest',axis=1)
s1.index=df5_grouped.index
# GROUPING BY DELIVERY WINDOW AND DESTINATION CLUSTER
df5_grouped = df_ord_product_dest_supp_pack5.groupby(['Requested Delivery Window', 'Destination Cluster','Supplier']).sum()
df5_grouped.columns
df5_grouped.drop(
            [
            'Packaging Capacity by Volume (cm3)',
            'Packaging Weight Limit (kg)',
            'SKU Weight (kg)',
            ],
        axis='columns', inplace=True
        )
df5_grouped
trucktype_df.columns

# SORT AND REINDEX
trucktype_sorted_by_vol = trucktype_df.sort_values(by=['Truck Capacity by Volume (m3)']).reset_index(drop=True)
# len(trucktype_sorted_by_vol)
# df5_grouped.columns

truck_vol = trucktype_sorted_by_vol['Truck Capacity by Volume (m3)']
truck_weight = trucktype_sorted_by_vol['FTL (Tons)']
truck_type = trucktype_sorted_by_vol['Truck Type']

# Initialise
vol_cond = []

# Create Conditions
for i in range(len(truck_vol)):
    print(i)
    print(truck_vol[i])
    vol_cond.append(
                    (df5_grouped['Total Weight (kg)'] <= truck_weight[i]*1000) \
                    &
                    (df5_grouped['Total Volume Capacity (m3)'] <= truck_vol[i])
                    )

df5_grouped['trucktype'] = np.select(vol_cond, truck_type)

df5_grouped.columns
