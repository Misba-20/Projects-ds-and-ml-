import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
data = {
    'Sales':[40,51,93,20,34,30,27,45,41,20],
    'Score':[89,66,54,52,99,65,86,50,89,78]
}
df = pd.DataFrame(data)
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(df)
df['Cluster'] = kmeans.labels_
print("Cluster Centers:\n", kmeans.cluster_centers_)
print("\nData with Cluster Labels:\n", df)
plt.figure(figsize=(8,6))
plt.scatter(df['Sales'], df['Score'],c=df['Cluster'], cmap='cool', s=100, label='Sales')
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],c='red', s=200, marker='X', label='Centroids')
plt.title('K-Means Clustering: Sales vs score')
plt.xlabel(' Sales')
plt.ylabel('score')
plt.legend()
plt.show()
