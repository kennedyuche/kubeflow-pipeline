import kfp
from kfp import dsl

def download_data_op():

    return dsl.ContainerOp(
        name='Download and Preprocess Data',
        image='kennedyuche/download-data:v1',
        arguments=[],
        file_outputs={
            'x_train': '/app/x_train.npy',
            'x_test': '/app/x_test.npy',
            'y_train': '/app/y_train.npy',
            'y_test': '/app/y_test.npy',
        }
    )

def train_op(x_train, y_train):

    return dsl.ContainerOp(
        name='Train Model',
        image='kennedyuche/train-model:v1',
        arguments=[
            '--x_train', x_train,
            '--y_train', y_train
        ],
        file_outputs={
            'model': '/app/model.pkl'
        }
    )

def test_op(x_test, y_test, model):

    return dsl.ContainerOp(
        name='Test Model',
        image='kennedyuche/test-model:v1',
        arguments=[
            '--x_test', x_test,
            '--y_test', y_test,
            '--model', model
        ],
        file_outputs={
            'accuracy': '/app/accuracy_output.txt'
        }
    )

def deploy_model_op(model):

    return dsl.ContainerOp(
        name='Deploy Model',
        image='kennedyuche/deploy-model:v1',
        arguments=[
            '--model', model
        ]
    )

@dsl.pipeline(
   name='Demo Pipeline',
   description='An example pipeline that trains and logs a regression model.'
)
def demo_pipeline():
    _download_data_op = download_data_op()
    
    _train_op = train_op(
        dsl.InputArgumentPath(_download_data_op.outputs['x_train']),
        dsl.InputArgumentPath(_download_data_op.outputs['y_train'])
    ).after(_download_data_op)

    _test_op = test_op(
        dsl.InputArgumentPath(_download_data_op.outputs['x_test']),
        dsl.InputArgumentPath(_download_data_op.outputs['y_test']),
        dsl.InputArgumentPath(_train_op.outputs['model'])
    ).after(_train_op)

    deploy_model_op(
        dsl.InputArgumentPath(_train_op.outputs['model'])
    ).after(_test_op)

client = kfp.Client()
client.create_run_from_pipeline_func(demo_pipeline, arguments={})