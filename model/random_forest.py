from sklearn.ensemble import RandomForestClassifier
import sys
sys.path.append('..')
from data_processor.grouping_processor import model_data_processor


model = RandomForestClassifier()

X_train, X_test, y_train, y_test = model_data_processor()
model.fit(X_train, y_train)
accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy}")
