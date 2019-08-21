"""
A model to predict the gender of a facebook user based on certain information
"""

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
import pandas as pd
import seaborn as sbn
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

class UserGender:

    def __init__(self):
        # import the dataset
        self.ld = pd.read_csv('friends_data.csv')
        # select the prediction target with dot notation
        self.y = self.ld.gender
        # select the features
        feat = [col for col in self.ld.columns]
        self.x = self.ld[feat]

        # list of categorical columns/data
        self.categorical_cols = [col for col in self.x.columns if self.x[col].dtype == 'object']
        # list of numerical cols/data
        self.numerical_cols = [col for col in self.x.columns if self.x[col].dtype != 'object']
        # split data into train and validation set
        self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(self.x, self.y, random_state = 1)
        # define some variables that will be used later
        self.numerical_transformer = self.categorical_transformer = self.preprocessor = None


    def preroccess(self):
        # preprocessing for numerical data
        self.numerical_transformer = SimpleImputer(strategy='constant')

        # preprocessing for categorical data
        self.categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
                    ])

        # bundle preprocessing for numerical and categorical data
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', self.numerical_transformer, self.numerical_cols),
                ('cat', self.categorical_transformer, self.categorical_cols)
            ])

    def log_reg(self):
        """
        logical regression model
        """
        # define the model
        log_mod = LogisticRegression(solver='lbfgs', random_state=2)
        # bundle preprocessing and modeling code in a pipeline
        my_pipeline = Pipeline(steps=[('preprocessor', self.preprocessor),
        ('model', log_mod)
        ])
        # preprocessing of training data, fit model
        my_pipeline.fit(self.x_train, self.y_train)
        # preprocessing of validation data get predictions
        pred = my_pipeline.predict(self.x_val)

        # evaluate the model
        score = mean_absolute_error(self.y_val, pred)
        print('MAE:', score)
        print('log_reg A.S: ', accuracy_score(self.y_val, pred, normalize = True))




# test suit
if __name__ == '__main__':
    l = UserGender()
    l.preroccess()
    l.log_reg()