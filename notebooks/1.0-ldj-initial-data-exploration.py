# %%
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn
import os
from sklearn.feature_selection import SelectKBest, f_classif, SelectFromModel
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import f1_score
from sklearn import ensemble
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm, model_selection
from sklearn import neighbors
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder

# %%
#--Importing dataset

# Change it to your absolut path
abs_path = str(Path().absolute())

df_users=pd.read_csv(abs_path+"/data/raw/usagers-2021.csv", sep=";")
df_places=pd.read_csv(abs_path+"/data/raw/lieux-2021.csv", sep=";", header=0, low_memory=False)
df_caract=pd.read_csv(abs_path+"/data/raw/caracteristiques-2021.csv", sep = ";", encoding='utf-8')
df_veh=pd.read_csv(abs_path + "/data/raw/vehicules-2021.csv", sep=";")


# %% [markdown]
# # DataSet Users 

# %%
#--Visualizing dataset users 

df_users.head(15)
df_users['grav'].value_counts(normalize=True)

# %%
#--Calculating the number of victims by accident 

nb_victim = pd.crosstab(df_users.Num_Acc, "count").reset_index()

print(nb_victim)

# %%
#-- Calculating the number of vehicles involved in the accident 
nb_vehicules = pd.crosstab(df_veh.Num_Acc, "count").reset_index()

# %%
#--Changing the number associated to injured to make more sens

df_users.grav.replace([1,2,3,4], [1,3,4,2], inplace = True)

# %%
#--Removing variables secu2 and secu3 because they don't bring anything relevant 
df_users.drop(["secu2", "secu3"], inplace=True, axis=1)

# %%
#--Adding the age of the victims at the time of the accident

#-Extracting the year of the accident thanks to the accident number
df_users["year_acc"] = df_users["Num_Acc"].astype(str).apply(lambda x : x[:4]).astype(int)

#-Calculating the age the victim
df_users["victim_age"] = df_users["year_acc"]-df_users["an_nais"]
for i in df_users["victim_age"] :
  #- Replacing outliers by NaN
  if (i>120)|(i<0):
    df_users["victim_age"].replace(i,np.nan)

df_users.drop(["year_acc","an_nais"], inplace=True, axis=1)

# %%
df_users.isna().sum()

# %% [markdown]
# # Dataset Caracteristics

# %%
df_caract.head()

# %%
#--Replacing column named agg by agg_ since agg is a Python method

df_caract.rename({"agg" : "agg_"},  inplace = True, axis = 1)

# %%
#--Replacing Corsica code 2A and 2B by 201 and 202 
corse_replace = {"2A":"201", "2B":"202"}
df_caract["dep"] = df_caract["dep"].str.replace("2A", "201")
df_caract["dep"] = df_caract["dep"].str.replace("2B", "202")
df_caract["com"] = df_caract["com"].str.replace("2A", "201")
df_caract["com"] = df_caract["com"].str.replace("2B", "202")

# %%
#--Creating a column datetime
df_caract['datetime_str'] = df_caract['jour'].astype(str) + '/' + df_caract['mois'].astype(str) + '/' + df_caract['an'].astype(str) + ' ' + df_caract['hrmn']
df_caract['datetime'] = pd.to_datetime(df_caract['datetime_str'], format='%d/%m/%Y %H:%M')
df_caract.drop(columns=['datetime_str'], inplace=True)
df_caract["datetime"].sort_values()


# %%
#--Creating a column hour that will replace hrmn

df_caract["hour"] = df_caract["hrmn"].astype(str).apply(lambda x : x[:-3])
df_caract.drop(['hrmn'], inplace=True, axis=1)

# %%
#--Convertir columns dep, com and hour into type int
df_caract[["dep","com", "hour"]] = df_caract[["dep","com", "hour"]].astype(int)


# %%
#--Converting columns lat and long into float type

dico_to_float = { 'lat': float, 'long':float}

df_caract["lat"] = df_caract["lat"].str.replace(',', '.')
df_caract["long"] = df_caract["long"].str.replace(',', '.')
df_caract = df_caract.astype(dico_to_float)

df_caract.dtypes

# %%
#--Removing variable adr because not usable

df_caract = df_caract.drop(columns = 'adr')

# %%
df_caract.shape

# %%
#--Grouping the modalities of the atm ( Atmosheric Conditions) variable into 1 : Risky and 0 : Normal. We include Other in Normal.
print("Modalities of the variable atm : ", df_caract['atm'].unique())
dico = {1:0, 2:1, 3:1, 4:1, 5:1, 6:1,7:1, 8:0, 9:0}
df_caract["atm"] = df_caract["atm"].replace(dico)
df_caract.head()

# %%
#--Visualizing correlations
df_numerical = df_caract.select_dtypes(include=['int64', 'float64', 'datetime'])

correlation_matrix = df_numerical.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation matrix')
plt.show()


# %% [markdown]
# # Dataset Vehicles 

# %%
df_veh.head()


# %%
df_veh.catv.unique()

# %%
df_veh.isna().sum()

# %% [markdown]
# # Merging datasets

# %%
df_users.head()

# %%
#--Merging datasets users and vehicles

fusion1= df_users.merge(df_veh, on = ["Num_Acc","num_veh", "id_vehicule"], how="inner")


# %%
#--Keeping 1 line by accident and keeping the most severe injured person

fusion1 = fusion1.sort_values(by = "grav", ascending = False)
fusion1 = fusion1.drop_duplicates(subset = ['Num_Acc'], keep="first")
fusion1.head()

# %%
fusion2 = fusion1.merge(df_places, on = "Num_Acc", how = "left")

# %%
df = fusion2.merge(df_caract, on = 'Num_Acc', how="left")

# %%
df.head()

# %%
#--Adding the number of victims
df = df.merge(nb_victim, on = "Num_Acc", how = "inner")

df.rename({"count" :"nb_victim"},axis = 1, inplace = True) 



# %%
#--Adding the number of vehicles 

df = df.merge(nb_vehicules, on = "Num_Acc", how = "inner") 
df.rename({"count" :"nb_vehicules"},axis = 1, inplace = True)

# %%
df['grav'].unique()

# %%
#--Modification of the target variable  : 1 : prioritary// 0 : non-prioritary

df['grav'].replace([2,3,4], [0,1,1], inplace=True)
df

# %%

#--Calculating the number of missing values for each column
missing_values_count = df.isnull().sum()

#--Calculating the percentage of missing values for each variables 
total_cells = len(df)
missing_percentage = (missing_values_count / total_cells) * 100

#--Creating a new dataframe with the percentage of missing values 
missing_df = pd.DataFrame({'Column': missing_percentage.index, 'MissingPercentage': missing_percentage.values})

missing_df = missing_df.sort_values(by='MissingPercentage', ascending=False)

print(missing_df)

# %%
#--Removing variables with more than 70% of missing values 
list_to_drop = ['v1', 'lartpc','occutc','v2','vosp','locp','etatp', 'infra', 'obs']

df.drop(list_to_drop, inplace=True, axis=1)

# %%
df.columns

# %%
catv_value = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,30,31,32,33,34,35,36,37,38,39,40,41,42,43,50,60,80,99]
catv_value_new = [0,1,1,2,1,1,6,2,5,5,5,5,5,4,4,4,4,4,3,3,4,4,1,1,1,1,1,6,6,3,3,3,3,1,1,1,1,1,0,0]
df['catv'].replace(catv_value, catv_value_new, inplace = True)

# %%
#--Replacing values -1 et 0 par NaN
col_to_replace0_na = ["actp", "trajet", "catv", "motor"]
col_to_replace1_na = ["actp", "trajet", "secu1", "catv", "obsm", "motor", "circ", "larrout", "surf", "situ", "vma", "atm", "col"]
df2 = df.copy()
df[col_to_replace1_na] = df[col_to_replace1_na].replace(-1, np.nan)
df[col_to_replace0_na] = df[col_to_replace0_na].replace(0, np.nan)

# %%
for column in df.columns[15:]:
    print(f"Modalities of the variable {column} : ", df[column].unique())

# %%
#--Removing variables that do not match with our goal to predict the severity of the accident 

list_to_drop = ['senc', 'manv', 'choc', 'nbv', 'prof', 'plan', 'Num_Acc', 'id_vehicule', 'num_veh', 'pr', 'pr1', 'trajet' ]
# ,'voie'
df.drop(list_to_drop, axis=1, inplace=True)

# %%
#--Replacing modalities A and B by 10 and 11
df["actp"] = df["actp"].str.replace("A","10")
df["actp"] = df["actp"].str.replace("B","11")
df["actp"] = df["actp"].astype(int)

# %%
df.select_dtypes(['object']).columns

# %%
df['voie'].unique()

# %%
#--Converting larrout into float
df["larrout"] = df["larrout"].str.replace(",",".")
df["larrout"] = df["larrout"].astype(float)

# %%
#--Fill NaN with mode 
col_to_fill_na = ["surf", "situ", "circ", "col", "motor"]

df[col_to_fill_na] = df[col_to_fill_na].fillna(df[col_to_fill_na].mode().iloc[0])


# %%
#Drop NaN 

df = df.dropna(axis=0)

# %%
# Finale version of the preprocessing steps :

#--Importing dataset
df_users=pd.read_csv(abs_path+"/data/raw/usagers-2021.csv", sep=";")
df_places=pd.read_csv(abs_path+"/data/raw/lieux-2021.csv", sep=";", header=0, low_memory=False)
df_caract=pd.read_csv(abs_path+"/data/raw/caracteristiques-2021.csv", sep = ";", encoding='utf-8')
df_veh=pd.read_csv(abs_path+"/data/raw/vehicules-2021.csv", sep=";")


nb_victim = pd.crosstab(df_users.Num_Acc, "count").reset_index()
nb_vehicules = pd.crosstab(df_veh.Num_Acc, "count").reset_index()
df_users["year_acc"] = df_users["Num_Acc"].astype(str).apply(lambda x : x[:4]).astype(int)
df_users["victim_age"] = df_users["year_acc"]-df_users["an_nais"]
for i in df_users["victim_age"] :
        if (i>120)|(i<0):
                df_users["victim_age"].replace(i,np.nan)
df_caract["hour"] = df_caract["hrmn"].astype(str).apply(lambda x : x[:-3])
df_caract.drop(['hrmn', 'an'], inplace=True, axis=1)
df_users.drop(['an_nais'], inplace=True, axis=1)

#--Replacing names 
df_users.grav.replace([1,2,3,4], [1,3,4,2], inplace = True)
df_caract.rename({"agg" : "agg_"},  inplace = True, axis = 1)
corse_replace = {"2A":"201", "2B":"202"}
df_caract["dep"] = df_caract["dep"].str.replace("2A", "201")
df_caract["dep"] = df_caract["dep"].str.replace("2B", "202")
df_caract["com"] = df_caract["com"].str.replace("2A", "201")
df_caract["com"] = df_caract["com"].str.replace("2B", "202")

#--Converting columns types
df_caract[["dep","com", "hour"]] = df_caract[["dep","com", "hour"]].astype(int)

dico_to_float = { 'lat': float, 'long':float}
df_caract["lat"] = df_caract["lat"].str.replace(',', '.')
df_caract["long"] = df_caract["long"].str.replace(',', '.')
df_caract = df_caract.astype(dico_to_float)


#--Grouping modalities 
dico = {1:0, 2:1, 3:1, 4:1, 5:1, 6:1,7:1, 8:0, 9:0}
df_caract["atm"] = df_caract["atm"].replace(dico)
catv_value = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,30,31,32,33,34,35,36,37,38,39,40,41,42,43,50,60,80,99]
catv_value_new = [0,1,1,2,1,1,6,2,5,5,5,5,5,4,4,4,4,4,3,3,4,4,1,1,1,1,1,6,6,3,3,3,3,1,1,1,1,1,0,0]
df_veh['catv'].replace(catv_value, catv_value_new, inplace = True)

#--Merging datasets 
fusion1= df_users.merge(df_veh, on = ["Num_Acc","num_veh", "id_vehicule"], how="inner")
fusion1 = fusion1.sort_values(by = "grav", ascending = False)
fusion1 = fusion1.drop_duplicates(subset = ['Num_Acc'], keep="first")
fusion2 = fusion1.merge(df_places, on = "Num_Acc", how = "left")
df = fusion2.merge(df_caract, on = 'Num_Acc', how="left")

#--Adding new columns
df = df.merge(nb_victim, on = "Num_Acc", how = "inner")
df.rename({"count" :"nb_victim"},axis = 1, inplace = True) 
df = df.merge(nb_vehicules, on = "Num_Acc", how = "inner") 
df.rename({"count" :"nb_vehicules"},axis = 1, inplace = True)

#--Modification of the target variable  : 1 : prioritary // 0 : non-prioritary
df['grav'].replace([2,3,4], [0,1,1], inplace=True)


#--Replacing values -1 and 0 
col_to_replace0_na = [ "trajet", "catv", "motor"]
col_to_replace1_na = [ "trajet", "secu1", "catv", "obsm", "motor", "circ", "surf", "situ", "vma", "atm", "col"]
df[col_to_replace1_na] = df[col_to_replace1_na].replace(-1, np.nan)
df[col_to_replace0_na] = df[col_to_replace0_na].replace(0, np.nan)


#--Dropping columns 
list_to_drop = ['senc','larrout','actp', 'manv', 'choc', 'nbv', 'prof', 'plan', 'Num_Acc', 'id_vehicule', 'num_veh', 'pr', 'pr1','voie', 'trajet',"secu2", "secu3",'adr', 'v1', 'lartpc','occutc','v2','vosp','locp','etatp', 'infra', 'obs' ]
df.drop(list_to_drop, axis=1, inplace=True)

#--Dropping lines with NaN values
col_to_drop_lines = ['catv', 'vma', 'secu1', 'obsm', 'atm']
df = df.dropna(subset = col_to_drop_lines, axis=0)

#--Filling NaN values
col_to_fill_na = ["surf", "circ", "col", "motor"]
df[col_to_fill_na] = df[col_to_fill_na].fillna(df[col_to_fill_na].mode().iloc[0])

target = df['grav']
feats = df.drop(['grav'], axis = 1)

X_train, X_test, y_train, y_test = train_test_split(feats, target, test_size=0.3, random_state = 42)

#--Filling NaN values
# col_to_fill_na = ["surf", "circ", "col", "motor"]
# X_train[col_to_fill_na] = X_train[col_to_fill_na].fillna(X_train[col_to_fill_na].mode().iloc[0])
# X_test[col_to_fill_na] = X_test[col_to_fill_na].fillna(X_train[col_to_fill_na].mode().iloc[0])

# %%
X_train.shape

# %%
# Select lines to run a gridsearch 
num_random_rows = 5000
X_train_reduced = X_train.sample(n=num_random_rows, random_state = 42)
X_train_reduced.shape
y_train_reduced = y_train.sample(n=num_random_rows, random_state = 42)

# %%
# Select best features for the median for categorical variables

selector_median = SelectFromModel(SGDClassifier(random_state = 0), threshold = 'median')

selector_median.fit_transform(X_train, y_train)

feats_sgdc_med = feats.columns[selector_median.get_support()]
print("les va les plus explicatives selectionnées par mediane sont:", feats.columns[selector_median.get_support()])

# %%
lr_select = LogisticRegression(class_weight='balanced')
lr_select.fit(X_train_reduced, y_train_reduced)

# Visualization of false positives and false negatives

y_pred_lr = lr_select.predict(X_test)

print(pd.crosstab(y_test, y_pred_lr, rownames=['Classe réelle'], colnames=['Classe prédite']))


# %%
f1_score_value = f1_score(y_test, y_pred_lr)

print("F1-score:", f1_score_value)

# %%
dt_clf = DecisionTreeClassifier(criterion = 'entropy', max_depth=4, random_state=123)

dt_clf.fit(X_train,y_train)

# %%

# Prediction of test features and creation of the confusion matrix
y_pred = dt_clf.predict(X_test)
pd.crosstab(y_test, y_pred, rownames=['Real class'], colnames=['Predict class'])
f1_score_value = f1_score(y_test, y_pred)

print("F1-score:", f1_score_value)

# %%
feats = {}
for feature, importance in zip(df.columns, dt_clf.feature_importances_):
    feats[feature] = importance 
    
importances = pd.DataFrame.from_dict(feats, orient='index').rename(columns={0: 'Importance'})
importances.sort_values(by='Importance', ascending=False).head(8)


# %%
dt_clf_gini = DecisionTreeClassifier(criterion='gini', max_depth=8, random_state=321)
dt_clf_gini.fit(X_train, y_train)
y_pred = dt_clf_gini.predict(X_test)
pd.crosstab(y_test, y_pred, rownames=['Real class'], colnames=['Predict class'])
f1_score_value = f1_score(y_test, y_pred)

print("F1-score:", f1_score_value)

# %%
knn = neighbors.KNeighborsClassifier(n_neighbors = 7, metric = 'minkowski')

knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)

print(f1_score(y_test, y_pred))

# %%
score_minko = []
score_man = []
score_cheb = []

for i in range(1, 10):
    knn_mink = neighbors.KNeighborsClassifier(n_neighbors = i, metric = 'minkowski').fit(X_train_reduced.values, y_train_reduced.values)
    knn_man = neighbors.KNeighborsClassifier(n_neighbors = i, metric = 'manhattan').fit(X_train_reduced.values, y_train_reduced.values)
    knn_cheb = neighbors.KNeighborsClassifier(n_neighbors = i, metric = 'chebyshev').fit(X_train_reduced.values, y_train_reduced.values)
    y_pred_mink = knn_mink.predict(X_test.values)
    y_pred_man = knn_man.predict(X_test.values)
    y_pred_cheb = knn_cheb.predict(X_test.values)
    score_minko.append(f1_score(y_test, y_pred_mink))
    score_man.append(f1_score(y_test, y_pred_man))
    score_cheb.append(f1_score(y_test, y_pred_cheb))

print(score_minko)

# %%
rf_classifier = ensemble.RandomForestClassifier(n_jobs=-1)

#--Train the model
rf_classifier.fit(X_train, y_train)

y_pred_rf = rf_classifier.predict(X_test)
f1 = f1_score(y_test, y_pred_rf)


X_test.head()


# %%
clf = ensemble.RandomForestClassifier()

# Définir la grille des hyperparamètres à explorer
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Créer l'objet GridSearchCV
grid_search = GridSearchCV(clf, param_grid, cv=5, scoring='f1')

# Effectuer la recherche sur la grille
grid_search.fit(X_train_reduced, y_train_reduced)

# Afficher les meilleurs paramètres et score
print("Meilleurs paramètres:", grid_search.best_params_)
print("Meilleur score F1:", grid_search.best_score_)

# Utiliser le modèle avec les meilleurs paramètres
best_clf = grid_search.best_estimator_
y_pred_rf = best_clf.predict(X_test)

# Calculer et afficher le score F1 sur les données de test
f1 = f1_score(y_test, y_pred_rf)
print("Score F1 sur les données de test:", f1)

# %%
dico = {"place": 0,
"catu": 0,
"sexe" : 0,
"secu1" : 0.0,
"year_acc" : 0,
"victim_age" : 0,
"catv" : 0,
"obsm" : 0,
"motor" : 0,
"catr" : 0,
"circ" : 0,
"surf" : 0,
"situ" : 0,
"vma" : 0,
"jour" :0,
"mois" : 0,
"lum" : 0,
"dep" : 0,
"com" : 0,
"agg_" : 0,
"int" : 0,
"atm" : 0,
"col" :0, 
"lat" : 0,
"long" : 0,
"hour" : 0,
"nb_victim" : 0,
"nb_vehicules" : 0}

df_test = pd.DataFrame([dico])
print(rf_classifier.predict(df_test))

# %%
# Supprimez la limite de lignes et de colonnes pour l'affichage
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
y_pred_rf
X_test.head()

# %%
import imblearn
from imblearn.over_sampling import RandomOverSampler, SMOTE


rOs = RandomOverSampler()
X_ro, y_ro = rOs.fit_resample(X_train, y_train)
print('Classes échantillon oversampled :', dict(pd.Series(y_ro).value_counts()))

#SMOTE
smo = SMOTE()
X_sm, y_sm = smo.fit_resample(X_train, y_train)
print('Classes échantillon SMOTE :', dict(pd.Series(y_sm).value_counts()))



