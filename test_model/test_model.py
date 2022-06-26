from bitarray import test
import numpy as np
import joblib
import argparse
from sklearn.metrics import accuracy_score

def test_model(x_test, y_test, model_path):
    # Load the test data
    x_test = np.load('x_test')
    y_test = np.load('y_test')
    
    # Load the trained model from the model training component
    model = joblib.load(model_path)

    # Get predictions
    y_pred = model.predict(x_test)
    
    # Get accuracy
    accuracy = accuracy_score(y_test, y_pred)

    # Save accuracy output into a text file
    with open('accuracy_output.txt', 'a') as file:
        file.write(str(accuracy))


if __name__ == '__main__':

    # Defining and parsing the command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--x_test')
    parser.add_argument('--y_test')
    parser.add_argument('--model')

    args = parser.parse_args()

    test_model(args.x_test, args.y_test, args.model)

    print('Model Testing ... 100% Complete')