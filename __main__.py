import click

import nnir.training.trainer as nt
import nnir.classifier as nc
import image.loader as iml
import image.writer as iw
import sound.loader as sl
import sound.writer as sw
import man.label_path_writer as mlpw

from config import *


class Config:
    def __init__(self):
        with open('tmp/opt') as temp:
            self.opt = temp.readline()


config = Config()

if config.opt == 'train':
    @click.command()
    @click.argument('sess_id', required=True)
    @click.argument('trained_model_path', required=True)
    @click.argument('trained_model_name', required=True)
    @click.option('--n_perceptrons_per_layer', default=(100, 51, 51, 51))
    @click.option('--optimizer', default='GradientDescent')
    @click.option('--n_epochs', default=150)
    @click.option('--learning_rate', default=0.2)
    @click.option('--train_test_split', default=0.1)
    def train(sess_id: int, trained_model_path: str, trained_model_name: str, n_perceptrons_per_layer: tuple,
              optimizer: str, n_epochs: int, learning_rate: float, train_test_split: float):
        trainer = nt.Train(sess_id, trained_model_path, trained_model_name,
                           optimizer=optimizer, n_perceptrons_layer=n_perceptrons_per_layer,
                           epochs=n_epochs, learning_rate=learning_rate, train_test_split=train_test_split, training_type='conv')
        trainer.train()
    train()

elif config.opt == 'im_man1':
    @click.command()
    @click.argument('dataset_name', required=True)
    @click.argument('method', required=True)
    @click.argument('file_name', required=True)
    def im_man_1(dataset_name, method: str, file_name: str):
        loader = iml.ImageLoader(dataset_name, method=method)
        data = loader.main()
        writer = iw.TrainingDataWriter(data, file_name, dataset_name)
        writer.main()
    im_man_1()

elif config.opt == "im_man2":
    @click.command()
    @click.argument('dataset_name', required=True)
    @click.argument('method', required=True)
    @click.argument('file_name', required=True)
    def im_man_2(dataset_name: str, method: str, file_name: str):
        loader = iml.ImageLoader(external_working_directory_path+'datasets/'+dataset_name+'/paths.txt', method=method)
        data = loader.main()
        writer = iw.TrainingDataGenWriter(dataset_name, file_name, data)
        writer.main()
    im_man_2()

elif config.opt == 'im_man3':
    @click.command()
    @click.argument('dataset_name', required=True)
    @click.argument('method', required=True)
    @click.argument('file_name', required=True)
    def im_man_3(dataset_name: str, method: str, file_name: str):
        loader = iml.ImageLoader(dataset_name, method=method)
        data = loader.main()
        writer = iw.DataWriter(data, file_name, dataset_name)
        writer.main()
    im_man_3()

# elif config.opt == 'im_man4':
#     @click.command()
#     @click.argument('path_file_path', required=True)
#     @click.argument('file_name', required=True)
#     @click.argument('label_file_path', required=True)
#     def im_man_4(path_file_path: str, file_name: str, label_file_path: str):
#         loader = iml.ConvNetsImageLoader(path_file_path)
#         data = loader.main()
#         writer = iw.TrainingDataWriter(data, file_name, label_file_path)
#         writer.main()
#     im_man_4()

elif config.opt == 'snd_man_1':
    @click.command()
    @click.argument('path_file_path')
    @click.argument('file_name')
    def snd_man_1(path_file_path, file_name):
        loader = sl.Loader(path_file_path)
        data = loader.main()
        writer = sw.DataWriter(data, file_name)
        writer.main()
    snd_man_1()

elif config.opt == 'snd_man_2':
    @click.command()
    @click.argument('path_file_path')
    @click.argument('label_file_path')
    @click.argument('file_name')
    def snd_man_2(path_file_path: str, label_file_path: str, file_name: str):
        loader = sl.Loader(path_file_path)
        data = loader.main()
        writer = sw.TrainDataWriter(data, file_name, label_file_path)
        writer.main()
    snd_man_2()

elif config.opt == 'classify':
    @click.command()
    @click.argument('sess_id', required=True)
    @click.argument('model_path', required=True)
    @click.argument('model_name', required=True)
    @click.argument('training_dataset_name', required=True)
    @click.argument('prediction_dataset_name', required=True)
    @click.option('--prediction_fname', default='predictions')
    @click.option('--show_image', default=True)
    def predict(sess_id: int, model_path: str, model_name: str, training_dataset_name: str, prediction_dataset_name,
                prediction_fname: str, show_image: str):
        if show_image == 'True' or show_image == 'true':
            show_image = True
        elif show_image == 'False' or show_image == 'false':
            show_image = False
        predicter = nc.Predict(sess_id, model_path, model_name, training_dataset_name, prediction_dataset_name,
                               prediction_fname=prediction_fname, show_im=show_image, prediction_type='conv')
        predicter.main()
    predict()
elif config.opt == 'write_paths':
    @click.command()
    @click.argument('main_directory_path')
    @click.argument('dataset_name')
    def path_writer(main_directory_path, dataset_name):
        mlpw.write_paths(main_directory_path, dataset_name)
    path_writer()
elif config.opt == 'write_labels':
    @click.command()
    @click.argument('main_directory_path')
    @click.argument('dataset_name')
    def label_writer(main_directory_path, dataset_name):
        mlpw.write_labels(main_directory_path, dataset_name)
    label_writer()

