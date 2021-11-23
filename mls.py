# ========importing necessary libraries============
import os 
import pandas as pd
import numpy as np
import seaborn as sn
import matplotlib.pyplot as plt
import sqlite3
#=====================================================

#=========== loading and merging datasets (mls salaries from 2007-2017)===========
csv_paths=[files for files in os.listdir() if files[-4:]==".csv" and files[0:3]=="mls"]
mls_salaries=pd.concat(map(pd.read_csv,csv_paths))
print(mls_salaries.head())

#========= generate years to add to the dataframe========
lengths=[]
for paths in csv_paths:
    lengths.append(len(pd.read_csv(paths)))
years=[year for year in range(2007,2018)]
add_years=np.repeat(years,[i for i in lengths])
mls_salaries["years"]=add_years
print(mls_salaries.head())

# ============checking dimensions of the datasets========
print("length of rows= ",mls_salaries.shape[0])
print("length of columns = ",mls_salaries.shape[1])




# =======excluding the first name and lastname columns=====
mls_salaries=mls_salaries.iloc[:,[0,3,4,5,6]]
print(mls_salaries.head())


# =====check whether there are columns with na values======
print(mls_salaries.isna().any())

#======= defining a function to reuses code  in replacing na with mean.=========
def replace_na_num(col): # numerical columns
    mean=col.mean()
    return col.fillna(value=mean,inplace=True)
replace_na_num(mls_salaries.base_salary) # replace na in base salary column
replace_na_num(mls_salaries.guaranteed_compensation)


# =====replace na in categorical columns with most frequent==========
def replace_na_cat(col):
    freq_dict={} # creating dictionary to add column as key and frequancy as value
    for vals in col:
        if vals in freq_dict:
            freq_dict[vals]+=1
        else:
            freq_dict[vals]=1
    return col.fillna(max(freq_dict,key=freq_dict.get),inplace=True)
replace_na_cat(mls_salaries.position)
replace_na_cat(mls_salaries.club)
print(mls_salaries.isna().any()) #confirm no na values


# =====sort the dataframe based on salary from the highest paid to lowest====
mls_salaries=mls_salaries.sort_values(by="base_salary",ascending=False)
print(mls_salaries.head())



# =====adding the cleaned data to a databse=====
columns=mls_salaries.columns
command='create table if not exists mls'+ f"{*columns,}"
con=sqlite3.connect("mls_salaries.db")
con1=con.cursor()
con1.execute(command)
con.commit()
mls_salaries.to_sql('mls',con,if_exists='replace')
if True:
    print("===data added successfully to mls_salaries.db===")




# =============group statistics===============================
statistics=[sum,np.mean,np.std,min,max]
def grouped_stat(columns,statistics):
    agg_dict={
        "base_salary":statistics,
        "guaranteed_compensation":statistics
    }
    agg=mls_salaries.groupby(columns,sort=True).agg(
            agg_dict
        )
    return agg
# calclates total,standard deviation,maximum,minimum and average for salary and guranteed compensation
year_group=grouped_stat(["years"],statistics)
print(year_group)
# ========summary statistics based on position of players=====
position_grouped=grouped_stat(["position"],statistics)
print(position_grouped)

# ==========summary statistics for clubs spending========
club_grouped=grouped_stat(["club"],statistics)
print(club_grouped)


# =========aggregates based on both position and clubs=====
# clubs spending on salary and compensation summary every year
club_years=grouped_stat(["years","club"],statistics)
# deposit the large dataframe to a csv file
club_years.to_csv("club_years_agg.csv")
print(club_years)

# ========changes in salary and compensation over the years====
fig,ax=plt.subplots(1,2,figsize=(20,10))
sn.lineplot(ax=ax[0],x="years",y="base_salary",data=mls_salaries)
ax[0].set_title("salary over the years")
sn.lineplot(ax=ax[1],x="years",y="guaranteed_compensation",data=mls_salaries)
ax[1].set_title("compensation over the years")
plt.show()

#  =========salary and compensation over the years on basis of playing position=====
fig,ax=plt.subplots(1,2,figsize=(20,10))
sn.lineplot(ax=ax[0],x="years",y="base_salary",hue="position",data=mls_salaries)
ax[0].set_title("salary over the years based on playing positions")
sn.lineplot(ax=ax[1],x="years",y="guaranteed_compensation",hue="position",data=mls_salaries)
ax[1].set_title("compensation over the years based on playing positions")
plt.show()


#========== visualising number of players in each position======
fig=plt.figure(figsize=(8,5))
sn.countplot(x="position",data=mls_salaries)
plt.title("number of players in each position")
plt.show()


# ========distribution of salaries ang guranteed compensations ====
fig,ax=plt.subplots(1,2,figsize=(20,10))
sn.histplot(ax=ax[0],x="base_salary",data=mls_salaries,kde=True)
ax[0].set_title("base salary distribution")
sn.histplot(ax=ax[1],x="guaranteed_compensation",data=mls_salaries,kde=True)
ax[1].set_title("guranteed compensation distribution")
plt.show()

#======= salary and compensation distribution over the years========
fig,ax=plt.subplots(1,2,figsize=(20,10))
sn.boxplot(ax=ax[0],x="years",y="base_salary",data=mls_salaries)
ax[0].set_title("salary distribution over the years")
sn.boxplot(ax=ax[1],x="years",y="guaranteed_compensation",data=mls_salaries)
ax[1].set_title("compensation distribution over the years")
plt.show()


# =========compare distribution of salaries based on positions and clubs=====
# also detecting outliers
fig,ax=plt.subplots(1,2,figsize=(40,20))
sn.boxplot(ax=ax[0],x="position",y="base_salary",data=mls_salaries)
ax[0].set_title("base salary distribution based on positions")
sn.boxplot(ax=ax[1],x="club",y="base_salary",data=mls_salaries)
ax[1].set_title("base salary distribution based on clubs")
plt.show()

# =========comparing compensations based on positions and clubs=========
fig,ax=plt.subplots(1,2,figsize=(30,10))
sn.boxplot(ax=ax[0],x="position",y="guaranteed_compensation",data=mls_salaries)
ax[0].set_title("guaranteed compensation based on positions")
sn.boxplot(ax=ax[1],x="club",y="guaranteed_compensation",data=mls_salaries)
ax[1].set_title("guaranteed compensation bases on clubs")
plt.show()


#=======================barplots===========================================
# which year has the highest/lowest salaries and compensation?
fig,ax=plt.subplots(1,2,figsize=(30,10))
sn.barplot(ax=ax[0],x="years",y="base_salary",data=mls_salaries)
ax[0].set_title("base salary over the years")
sn.barplot(ax=ax[1],x="years",y="guaranteed_compensation",data=mls_salaries)
ax[1].set_title("guaranteed compensation over the years")
plt.show()

# comparing salary and compensations paid by clubs
#comparing salary and compensations received in terms of positions
fig,ax=plt.subplots(2,2,figsize=(30,10))
sn.barplot(ax=ax[0,0],x="position",y="base_salary",data=mls_salaries)
ax[0,0].set_title("base salary based positions")
sn.barplot(ax=ax[0,1],x="position",y="guaranteed_compensation",data=mls_salaries)
ax[0,1].set_title("guaranteed compensation based on  position")
sn.barplot(ax=ax[1,0],x="club",y="base_salary",data=mls_salaries)
ax[1,0].set_title("base salary paid by clubs")
sn.barplot(ax=ax[1,1],x="club",y="guaranteed_compensation",data=mls_salaries)
ax[1,1].set_title("guaranteed compensation paid by clubs")
plt.show()



#============ display correlation between salary and compensation=============
fig=plt.figure(figsize=(10,5))
sn.heatmap(np.corrcoef(mls_salaries.base_salary,mls_salaries.guaranteed_compensation),linewidth=0.5,cmap="plasma")
plt.title("correlation between salary and compensation")
plt.show()

# ===========investigating relationship between salary and compensation==========
fig,(ax,axs)=plt.subplots(1,2,figsize=(20,5))
fig.suptitle("base salary vs compensation")
sn.scatterplot(x="base_salary",y="guaranteed_compensation",data=mls_salaries,ax=ax)
sn.scatterplot(x="base_salary",y="guaranteed_compensation",hue="position",data=mls_salaries,ax=axs)
plt.show()



#=============regression plot for base salary and guaranteed compensation based on positions======
fig=plt.figure(figsize=(20,10))
sn.lmplot(x="base_salary",y="guaranteed_compensation",hue="position",data=mls_salaries,height=10)
plt.title("regression plot for salary and compensation")
plt.show()


#regression plot for base salary and guaranteed compensation in terms of clubs
fig=plt.figure(figsize=(20,10))
sn.lmplot(x="base_salary",y="guaranteed_compensation",hue="club",data=mls_salaries,height=10)
plt.title("regression plot for salary and compensation")
plt.show()

# ==========showing distribution and regression for salary and compensation=============
fig=plt.figure(figsize=(10,10))
sn.jointplot(x="base_salary",y="guaranteed_compensation",data=mls_salaries,kind="reg",height=10)
plt.show()






