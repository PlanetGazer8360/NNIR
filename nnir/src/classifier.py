import tensorflow as tf
import numpy as np
import json

from src.pcontrol import *
from src.config import *

from src.neural_network_models.convolutional_neural_network import convolutional_neural_network

from src.image.display import display_image


class Predict:
    def __init__(self,
                 sess_id: int,
                 model_path,
                 model_name,
                 training_dataset_name,
                 prediction_dataset_name,
                 prediction_fname='predictions',
                 show_im: bool=True):
        self.id = sess_id
        self.model_path = model_path
        self.model_name = model_name
        self.training_dataset_name = training_dataset_name
        self.prediction_dataset_name = prediction_dataset_name
        self.prediction_fname = prediction_fname
        self.show_im = show_im

        self.raw_predictions = []
        self.predictions = []
        self.Meta = MetaData()
        raw_meta = self.Meta.read('n_columns', 'data_path', 'width', 'height', sess_id=sess_id)

        meta = [mt for mt in raw_meta]

        self.n_columns = meta[0]
        self.dpath = meta[1]
        self.width = int(meta[2])
        self.height = int(meta[3])

        ppath = external_working_directory_path+'predictions/'+self.prediction_dataset_name
        if not os.path.exists(ppath):
            os.mkdir(ppath)
            if not os.path.exists(ppath+'/'+self.training_dataset_name):
                os.mkdir(ppath+'/'+self.training_dataset_name)
        self.pfnames = [external_working_directory_path+'predictions/'+self.prediction_dataset_name + '/' +
                        self.training_dataset_name + '/' + self.prediction_fname + '.csv',
                        external_working_directory_path+'predictions/'+self.prediction_dataset_name + '/' +
                        self.training_dataset_name + '/' + self.prediction_fname + '_pathfile.csv']

    def read_dataset(self):
        sess = tf.Session()
        df = pd.read_csv(self.dpath, header=None)
        X = df[df.columns].values
        X = sess.run(tf.reshape(X, [X.shape[0], self.height, self.width, 3]))

        print(X.shape, "X shape")

        return X

    def restore_model(self, sess):
        # Create saver object
        saver = tf.train.import_meta_graph(
            external_working_directory_path + self.model_path + self.model_name + '.meta')

        # Attempt to restore model for prediction
        saver.restore(sess, tf.train.latest_checkpoint(external_working_directory_path + self.model_path + './'))
        print("Trained model has been restored successfully!")

        w1, w2, w3, w4 = sess.run(('conv_weights1:0', 'conv_weights2:0', 'fcl_weights3:0', 'out_weights4:0'))
        b1, b2, b3, b4 = sess.run(('conv_biases1:0', 'conv_biases2:0', 'fcl_biases3:0', 'out_biases4:0'))

        weights = {
            'conv_weights1': tf.convert_to_tensor(w1),
            'conv_weights2': tf.convert_to_tensor(w2),
            'fcl_weights3': tf.convert_to_tensor(w3),
            'out_weights4': tf.convert_to_tensor(w4)
        }

        biases = {
            'conv_biases1': tf.convert_to_tensor(b1),
            'conv_biases2': tf.convert_to_tensor(b2),
            'fcl_biases3': tf.convert_to_tensor(b3),
            'out_biases4': tf.convert_to_tensor(b4)
        }
        return weights, biases

    def predict(self):
        sess = tf.Session()

        x = tf.placeholder(tf.float32, [None, self.height, self.width, 3])

        weights, biases = self.restore_model(sess)

        model = convolutional_neural_network(x, weights, biases)

        prediction = sess.run(model, feed_dict={x: self.read_dataset()})
        print(prediction.shape)

        pred_labels_int = np.ndarray.tolist(sess.run(tf.argmax(prediction, 1)))
        self.raw_predictions = pred_labels_int

        self.int_to_label()
        self.write_predictions()

    def int_to_label(self):
        assigned_labels, names = self.label_assigner()

        for raw_prediction in self.raw_predictions:
            for pred_char, pred_int in assigned_labels.items():
                if raw_prediction == pred_int:
                    self.predictions.append([names[pred_int]])

        return self.predictions

    def label_assigner(self):
        int_to_label = {}

        with open(external_working_directory_path+'datasets/'+self.training_dataset_name+'/obj_labels.json', 'r') as ol:
            data = json.load(ol)
            for ln, item in enumerate(sorted(data.values())):
                int_to_label[item] = ln

        return int_to_label, list(data.keys())

    def write_predictions(self):
        # Re-write data in addition to predicted labels in CSV file; filename is a parameter
        data = list(self.read_dataset())
        data = [list(dt) for dt in data]

        for pix_data_n in range(len(data)):
            data[pix_data_n].append(self.predictions[pix_data_n][0])

        with open(self.pfnames[0], 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for im_pix_data in data:
                writer.writerow(im_pix_data)

        # Write image paths together with predicted labels in CSV file
        raw_meta = self.Meta.read('data_path', sess_id=self.id)

        meta = [mt for mt in raw_meta]

        df = pd.read_csv(meta[0], header=None)

        raw_rows = df.iterrows()
        rows = []
        for index, row in raw_rows:
            rows.append(list(row.values))

        df = pd.read_csv('meta/sess/'+str(self.id)+'/impaths.csv', header=None)

        raw_rows = df.iterrows()
        paths = []
        for _, row in raw_rows:
            paths.append(list(row)[0])

        with open(self.pfnames[1], 'w') as pathfile:
            writer = csv.writer(pathfile, delimiter=',')
            for n in range(len(paths)):
                if self.show_im is True:
                    display_image(self.predictions[n][0], paths[n])
                writer.writerow([paths[n], self.predictions[n][0]])

    def main(self):
        self.predict()
        self.Meta.write(self.id, used_model_path__output=external_working_directory_path +
                        self.model_path + '___' +
                        os.getcwd()+'/'+self.pfnames[0] +
                        '__'+os.getcwd()+'/'+self.pfnames[1])
