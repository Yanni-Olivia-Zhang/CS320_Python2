# project: p7
# submitter: yzhang2232
# partner: none
# hours: 3

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import PolynomialFeatures,StandardScaler
from sklearn.linear_model import LogisticRegression

class UserPredictor:
    def __init__(self):
        self.pipe = Pipeline([
            ("poly", PolynomialFeatures(degree = 2)),
            ("std", StandardScaler()),
            ("lr", LogisticRegression())       
        ])
        self.xcols = ["age", "past_purchase_amt", "seconds"]
        
    def clean(self,users,logs):
        clean = logs.groupby(['user_id',"url"]).sum('seconds').reset_index()
        clean = clean[clean['url'].str.contains('laptop')]
        users = pd.merge(left = users, right = clean, how = "left").fillna(0)
        return users
        
    def fit(self,users,logs,y):
        users = self.clean(users,logs)
        self.pipe.fit(users[self.xcols], y['y'])
        scores = cross_val_score(self.pipe, users[self.xcols], y["y"])
        print(f"AVG: {scores.mean()}, STD: {scores.std()}\n")
      
    def predict(self,users,logs):      
        users = self.clean(users,logs)
        return self.pipe.predict(users[self.xcols])        