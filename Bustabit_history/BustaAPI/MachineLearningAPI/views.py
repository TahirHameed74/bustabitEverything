from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.core import serializers
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from . models import anomaly
from . serializers import anomalySerializers
import pickle
import joblib
import json
import numpy as np
from sklearn import preprocessing
import pandas as pd

import os, uuid, sys
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings
from azure.identity import ClientSecretCredential
from io import StringIO
from kneed import KneeLocator
import sys
import matplotlib.dates as md
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from mpl_toolkits.mplot3d import Axes3D
import pickle
import os


class AnomalyView(viewsets.ModelViewSet):
	queryset = anomaly.objects.all()
	serializer_class = anomalySerializers
		
@api_view(["POST"])
def timeseriesmodel(request):
	try:
		
		outliers_fraction = 0.01 #Will be changed later with user needs
		dims = 2 #For PCA

		data = request.data #Returns Python Dictionary object

		#These values will come from AlgoPlus Frontend
		timeseries= data["data"]["time"]
		value= data["data"]["value"]
		container= data["file"]["container"]
		directory= data["file"]["directory"]
		filename= data["file"]["name"]
		istrain_flag= data["settings"]["istrain"]

        # Connection To Azure Datalake gen 2
		storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
		client_id = os.getenv('CLIENT_ID')
		client_secret = os.getenv('CLIENT_SECRET')
		tenant_id = os.getenv('TENANT_ID')


		credential = ClientSecretCredential(tenant_id, client_id, client_secret)

		service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format( "https", storage_account_name), credential=credential)
		

		file_system_client = service_client.get_file_system_client(file_system=container) #Passing container name

		directory_client = file_system_client.get_directory_client(directory) #Passing Directory name

		file_client = directory_client.get_file_client(filename) #Passing filename

		download = file_client.download_file()  #Downloads file from Datalake

		downloaded_bytes = download.readall()
		        
		s=str(downloaded_bytes,'utf-8')

		data = StringIO(s) 

		data = pd.read_csv(data) #Conversion to Dataframe

		directory_name='model01'
		output_pickle = directory_name + "/output_pickle.pkl"


		if(istrain_flag=='1'):

			if not os.path.exists(directory_name):
				os.makedirs(directory_name)


        # FEATURE ENGINEERING
			df1 = data[[timeseries,value]].copy()
			df1['Datetime'] = pd.to_datetime(df1[timeseries],format='%Y-%m-%d')
			df1.sort_values(by=['Datetime'], inplace=True)
			df1['month']=df1['Datetime'].dt.month 
			df1['day']=df1['Datetime'].dt.day
			df1['week']=df1['Datetime'].dt.week
			df1['dayofweek_num']=df1['Datetime'].dt.dayofweek  
			df1['quarter']=df1['Datetime'].dt.quarter
			df1['time_lag_1'] = df1[value].shift(1)
			df1['time_lag_2'] = df1[value].shift(2)
			df1.dropna(inplace=True)
			df1['rolling_mean'] = df1[value].rolling(window=4).mean()
			df1['rolling_median'] = df1[value].rolling(window=4).median()
			df1.dropna(inplace=True)
			df1['isWEEKDAY'] = np.where(df1['dayofweek_num']<5,1,0)
			df1['isWEEKEND'] = np.where(df1['dayofweek_num']>=5,1,0)
			del df1['Datetime']

			# Kmeans - Clustering
			result =df1.copy()
			data = df1.copy()
			data= data.drop([timeseries], axis=1)
			n_cluster = range(1, 20)
			kmeans = [KMeans(n_clusters=i).fit(data) for i in n_cluster]
			scores = [kmeans[i].score(data) for i in range(len(kmeans))]
			kneedle = KneeLocator(n_cluster, scores, S=1, curve='concave', direction='increasing')
			X = df1.copy()
			X = X.drop([timeseries], axis=1)
			X = X.values
			X_std = StandardScaler().fit_transform(X)
			data = pd.DataFrame(X_std)
			# reduce to 2 important features
			pca = PCA(n_components=dims)
			data = pca.fit_transform(data)
			# standardize these 2 new features
			scaler = StandardScaler()
			np_scaled = scaler.fit_transform(data)
			data = pd.DataFrame(np_scaled)
			result['principal_feature1'] = data[0]
			result['principal_feature2'] = data[1]
			km = KMeans(n_clusters=kneedle.knee)
			kmeans=km.fit(data)

			KMeans_model_pickle = directory_name + "/KMeans_model_pickle.pkl"
			with open(KMeans_model_pickle, "wb") as f:
				pickle.dump(kmeans, f)

			result['cluster'] = kmeans.predict(data)

			distance = pd.Series()
			model = kmeans
			# get the distance between each point and its nearest centroid. The biggest distances are considered as anomaly
			for i in range(0,len(data)):
				Xa = np.array(data.loc[i])
				Xb = model.cluster_centers_[model.labels_[i]-1]
				distance.set_value(i, np.linalg.norm(Xa-Xb))

			number_of_outliers = int(outliers_fraction*len(distance))
			threshold = distance.nlargest(number_of_outliers).min()
			# anomaly1 contain the anomaly result of the above method Cluster (0:normal, 1:anomaly) 
			result['anomaly1'] = (distance >= threshold).astype(int)
			result.dropna(inplace=True)

	        # ISOLATION FOREST
			data = df1.copy()
			data = data.drop([timeseries], axis=1)
			scaler = StandardScaler()
			np_scaled = scaler.fit_transform(data)
			data = pd.DataFrame(np_scaled)
			# train isolation forest
			model =  IsolationForest(contamination=outliers_fraction)
			model.fit(data)

			ISOLATION_FOREST_model_pickle = directory_name + "/ISOLATION_FOREST_model_pickle.pkl"
			with open(ISOLATION_FOREST_model_pickle, "wb") as f:
				pickle.dump(model, f)

			result['anomaly2'] = pd.Series(model.predict(data))

	   
	        # ONECLASS-SVM
			data = df1.copy()
			data= data.drop([timeseries], axis=1)
			scaler = StandardScaler()
			np_scaled = scaler.fit_transform(data)
			data = pd.DataFrame(np_scaled)
			# train oneclassSVM 
			model = OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.01)
			model.fit(data)

			OneClassSVM_model_pickle = directory_name + "/OneClassSVM_model_pickle.pkl"
			with open(OneClassSVM_model_pickle, "wb") as f:
				pickle.dump(model, f)

			result['anomaly3'] = pd.Series(model.predict(data))

			# RESULTS FINALIZING
			result["anomaly1"].replace({0: 1, 1: -1}, inplace=True)
			result["anomaly_1"] = result["anomaly1"].astype(int)
			result["anomaly_2"] = result["anomaly2"].astype(int)
			result["anomaly_3"] = result["anomaly3"].astype(int)

			del result['anomaly1']
			del result['anomaly2']
			del result['anomaly3']

			result_f = result[[timeseries,value,'anomaly_1','anomaly_2','anomaly_3']].copy()

			#result_f.to_json('temp.json', orient='records', lines=True)

			final_df = result_f.query('anomaly_1==-1 or anomaly_2==-1 or anomaly_3==-1')

			scores_list = []

			for index, row in final_df.iterrows():
				score=0
				if(row['anomaly_1']==-1):
					score=score+1
				if(row['anomaly_2']==-1):
					score=score+1
				if(row['anomaly_3']==-1):
					score=score+1

				scores_list.append(score)

			final_df['confidence'] = scores_list


			final_df_pickle = directory_name + "/final_df_pickle.pkl"
			with open(final_df_pickle, "wb") as f:
				pickle.dump(final_df, f)


			final_df = final_df[[timeseries, value, 'confidence']]

			out = final_df.to_json(orient='records')[1:-1].replace('},{', '} {')


			
			with open(output_pickle, "wb") as f:
				pickle.dump(out, f)


		elif(istrain_flag=='0'):
			with open(output_pickle, 'rb') as handle:
				output_loaded = pickle.load(handle)

			out = output_loaded



		return JsonResponse(out, safe=False)
	except ValueError as e:
		return Response(e.args[0], status.HTTP_400_BAD_REQUEST)
