def getDistanceByPoint(data, model):
    try:
        distance = pd.Series()
        for i in range(0,len(data)):
            Xa = np.array(data.loc[i])
            Xb = model.cluster_centers_[model.labels_[i]-1]
            distance.set_value(i, np.linalg.norm(Xa-Xb))
        return distance
    except Exception as e:
        print(e)

def reduce_dimensions(df1,dims,result):
    try:
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
        return data
    except Exception as e:
        print(e)

def kmeans_clustering(df1,outliers_fraction,result):
    
    try:  
        data = df1.copy()
        data= data.drop([timeseries], axis=1)
        n_cluster = range(1, 20)
        kmeans = [KMeans(n_clusters=i).fit(data) for i in n_cluster]
        scores = [kmeans[i].score(data) for i in range(len(kmeans))]
        kneedle = KneeLocator(n_cluster, scores, S=1, curve='concave', direction='increasing')
        data = reduce_dimensions(df1,dimensions,result)
        km = KMeans(n_clusters=kneedle.knee)
        kmeans=km.fit(data)
        result['cluster'] = kmeans.predict(data)
        
        # get the distance between each point and its nearest centroid. The biggest distances are considered as anomaly
        distance = getDistanceByPoint(data, kmeans)
        number_of_outliers = int(outliers_fraction*len(distance))
        threshold = distance.nlargest(number_of_outliers).min()
        # anomaly1 contain the anomaly result of the above method Cluster (0:normal, 1:anomaly) 
        result['anomaly1'] = (distance >= threshold).astype(int)
        result.dropna(inplace=True)
        
    except Exception as e:
        print(e)


def isolation_forest(df1,outliers_fraction,result):
    
    try:  
        data = df1.copy()
        data = data.drop([timeseries], axis=1)
        scaler = StandardScaler()
        np_scaled = scaler.fit_transform(data)
        data = pd.DataFrame(np_scaled)
        # train isolation forest
        model =  IsolationForest(contamination=outliers_fraction)
        model.fit(data)
        result['anomaly2'] = pd.Series(model.predict(data))
        
    
    except Exception as e:
        print(e)


def oneclass_svm(df1,outliers_fraction,result):
    
    try:  
        data = df1.copy()
        data= data.drop([timeseries], axis=1)
        scaler = StandardScaler()
        np_scaled = scaler.fit_transform(data)
        data = pd.DataFrame(np_scaled)
        # train oneclassSVM 
        model = OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.01)
        model.fit(data)
 
        result['anomaly3'] = pd.Series(model.predict(data))
        
    
    except Exception as e:
        print(e)

