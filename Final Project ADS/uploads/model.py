import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import os
import pickle
#%matplotlib inline
import imblearn
from imblearn.pipeline import make_pipeline as make_pipeline_imb
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss
from imblearn.metrics import classification_report_imbalanced
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, accuracy_score, classification_report
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.naive_bayes import BernoulliNB 
from sklearn.metrics import *
import zipfile
from zipfile import ZipFile
from urllib.request import urlopen
from io import BytesIO
import glob
import logging
import datetime
import time
import boto
import boto.s3
from boto.s3.key import Key 

dataset = pd.read_excel('E:\ADS\default+of+credit+card+clients.xlsx',header=1)

def check_missing_values(dataset):
    c = dataset.isnull().sum()
    c.to_frame().reset_index()
    for i in range(0, 25):
        
        if(c[i] == 0):
            continue
        else:
            print("Missing value present")
            return False
    return True

def replacing_missing_values(dataset):
	data = check_missing_values(dataset)
	print("yo")
	if(data == False):
	    new_data = pd.DataFrame()
	    dataset['limit_bal'].dropna(inplace = True)
	    dataset['sex'].dropna(inplace = True)
	    dataset['education'].dropna(inplace = True)
	    dataset['marriage'].dropna(inplace = True)
	    dataset['age'].dropna(inplace = True)
	    new_data = dataset
	    return new_data
	else:
	    return dataset

def feature_engineering(dataset):
    dataset = replacing_missing_values(dataset)
    print("yo1")
    dataset.rename(columns={'PAY_0':'PAY_1','default payment next month':'next_month_payment'},inplace=True)
    dataset.columns = map(str.lower, dataset.columns)
    filedu = (dataset.education == 5)|(dataset.education == 6)|(dataset.education == 0)
    dataset.loc[filedu,'education'] = 4  
    filmarra = (dataset.marriage == 0)
    dataset.loc[filmarra,'marriage'] = 3
    fil = (dataset.pay_1 == -2) | (dataset.pay_1 == -1) | (dataset.pay_1 == 0)
    dataset.loc[fil, 'pay_1'] = 0
    fil = (dataset.pay_2 == -2) | (dataset.pay_2 == -1) | (dataset.pay_2 == 0)
    dataset.loc[fil, 'pay_2'] = 0
    fil = (dataset.pay_3 == -2) | (dataset.pay_3 == -1) | (dataset.pay_3 == 0)
    dataset.loc[fil, 'pay_3'] = 0
    fil = (dataset.pay_4 == -2) | (dataset.pay_4 == -1) | (dataset.pay_4 == 0)
    dataset.loc[fil, 'pay_4'] = 0
    fil = (dataset.pay_5 == -2) | (dataset.pay_5 == -1) | (dataset.pay_5 == 0)
    dataset.loc[fil, 'pay_5'] = 0
    fil = (dataset.pay_6 == -2) | (dataset.pay_6 == -1) | (dataset.pay_6 == 0)
    dataset.loc[fil, 'pay_6'] = 0
    dataset['AgeBin'] = pd.cut(dataset['age'], 6, labels = [1,2,3,4,5,6])
    dataset['AgeBin'] = pd.to_numeric(dataset['AgeBin'])
    return dataset

def split_dataset(dataset):
    data = feature_engineering(dataset)
    print("yo2")
    X = data[['id', 'limit_bal', 'sex', 'education', 'marriage', 'age', 'pay_1',
       'pay_2', 'pay_3', 'pay_4', 'pay_5', 'pay_6', 'bill_amt1', 'bill_amt2',
       'bill_amt3', 'bill_amt4', 'bill_amt5', 'bill_amt6', 'pay_amt1',
       'pay_amt2', 'pay_amt3', 'pay_amt4', 'pay_amt5', 'pay_amt6']]

    y = data['next_month_payment']
    return X, y

def sampling(dataset):
    X,y  = split_dataset(dataset)
    print("yo3")
    sm = SMOTE(random_state=12, ratio = 1.0)
    x_res, y_res = sm.fit_sample(X, y)
    return x_res,y_res

def train_test(dataset):
    x_res, y_res = sampling(dataset)
    print("yo4")
    x_train_res, x_val_res, y_train_res, y_val_res = train_test_split(x_res,
                                                    y_res,
                                                    test_size = .2,
                                                    random_state=12)
    return x_train_res, x_val_res, y_train_res, y_val_res
    
def models(dataset):
	model = [
			RandomForestClassifier(n_estimators=40, max_depth=10),
			KNeighborsClassifier(n_neighbors=4),
			LogisticRegression(),
			BernoulliNB(),
			ExtraTreesClassifier(n_estimators = 500 , random_state = 123)
            ]
    with open('model.pckl', 'wb') as filename:
		for models in model:
			print("loop")
			pickle.dump(models, filename)
			print("dumped")
	return models

def fit_model(model, dataset):
    x_train_res, x_val_res, y_train_res, y_val_res = train_test(dataset)
    print("yo5")
    model.fit(x_train_res,y_train_res)
    prediction = model.predict(x_val_res)
    f1score = f1_score(y_val_res, prediction)
    accuracy = accuracy_score(y_val_res, prediction)
    cm = confusion_matrix(y_val_res, prediction)
    tp = cm[0][0]
    fp = cm[0][1]
    fn = cm[1][0]
    tn = cm[1][1]
    
    return f1score,accuracy,tp,fp,fn,tn

def accuracyscore(dataset):
    models = []
    #here = os.path.dirname(os.path.abspath(__file__))
    with open('model.pckl', 'rb') as filename:
        while True:
            try:
                print("trying")
                models.append(pickle.load(filename))
                print("appended")
            except EOFError:
                break
    print(models)
    accuracy =[]
    model_name =[]
    f1score = []
    true_positive =[]
    false_positive =[]
    true_negative =[]
    false_negative =[]
    for i in range(0,len(models)):
        f,a,tp,fp,fn,tn = fit_model(models[i],dataset)
        model_name.append(str(models[i]).split("(")[0])
        f1score.append(f)
        accuracy.append(a)
        #matrix.append(cm)
        true_positive.append(tp) 
        false_positive.append(fp)
        true_negative.append(fn) 
        false_negative.append(tn)    
    return model_name,f1score,accuracy,true_positive,false_positive,true_negative,false_negative


def performance_metrics(dataset):
    summary2 = accuracyscore(dataset)
    print("yo7")
    describe1 = pd.DataFrame(summary2[0],columns = {"Model_Name"})
    describe2 = pd.DataFrame(summary2[1],columns = {"F1_score"})
    describe3 = pd.DataFrame(summary2[2], columns ={"Accuracy_score"})
    describe4 = pd.DataFrame(summary2[3], columns ={"True_Positive"})
    describe5 = pd.DataFrame(summary2[4], columns ={"False_Positive"})
    describe6 = pd.DataFrame(summary2[5], columns ={"True_Negative"})
    describe7 = pd.DataFrame(summary2[6], columns ={"False_Negative"})
    des = describe1.merge(describe2, left_index=True, right_index=True, how='inner')
    des = des.merge(describe3,left_index=True, right_index=True, how='inner')
    des = des.merge(describe4,left_index=True, right_index=True, how='inner')
    des = des.merge(describe5,left_index=True, right_index=True, how='inner')
    des = des.merge(describe6,left_index=True, right_index=True, how='inner')
    des = des.merge(describe7,left_index=True, right_index=True, how='inner')
    final_csv = des.sort_values(ascending=False,by="Accuracy_score").reset_index(drop = True)
    return final_csv


final_csv = performance_metrics(dataset)
final_csv.to_csv(str(os.getcwd()) + "/accuracy_error_metrics.csv")  
AWS_ACCESS_KEY_ID = input("AWS_ACCESS_KEY_ID=")
AWS_SECRET_ACCESS_KEY = input("AWS_SECRET_ACCESS_KEY=")
conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
logger.info("Connected to S3")
print("Connected to S3")
'''
except:
	logger.info("Amazon keys are invalid")
	print("Amazon keys are invalid")
	exit()
'''

#Location for the region
loc=boto.s3.connection.Location.default

try:
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts)    
	bucket_name = AWS_ACCESS_KEY_ID.lower()+str(st).replace(" ", "").replace("-", "").replace(":","").replace(".","")
	bucket = conn.create_bucket(bucket_name, location=loc)
	filename = ('models.zip')
	logger.info("S3 bucket successfully created")


	#Uploading files to the Bucket
	def percent_cb(complete, total):
		sys.stdout.write('.')
		sys.stdout.flush()

	k = Key(bucket)
	k.key = 'Problem2'
	k.set_contents_from_filename(filename, cb=percent_cb, num_cb=10)

	logger.info("Model successfully uploaded to S3")
	print("Model successfully uploaded to S3")
except Exception as e:
	logger.error(str(e))
	exit()