import argparse
import joblib
import numpy as np

from sklearn.linear_model import LogisticRegression

def train_model(x_train, y_train):
    # Load the output data from the data_download component
    # This will serve as the input to this component
    x_train = np.load('x_train')
    y_train = np.load('y_train')
    
    # Initialize Logistic Regression model
    model = LogisticRegression()

    # Train model
    model.fit(x_train, y_train)

    # Save the model in .pkl format
    # This will serve as the output of this component
    joblib.dump(model, 'model.pkl')



if __name__ == '__main__':
    # Defining and parsing the command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--x_train')
    parser.add_argument('--y_train')
    args = parser.parse_args()
    train_model(args.x_train, args.y_train)
    print('Model Training ... 100% Complete')