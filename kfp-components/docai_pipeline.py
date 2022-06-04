import kfp
import kfp.dsl as dsl
from kfp.components import load_component_from_file

# Load pipeline components
create_spark_app_op = load_component_from_file('spark_delta_comp.yaml')

create_data_loader_op = load_component_from_file('data_loader_comp.yaml')

# Define the pipeline

@dsl.pipeline(
    name='docai data pipeline',
    description='Load 10k files to Azure storage, run spark job to pick the data and load back to Azure Storage in delta format'
)
def docai_data_pipeline():
    step1 = create_data_loader_op()

    step2 = create_spark_app_op().after(step1)

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(pipeline_func=docai_data_pipeline, package_path='docai_data_pipeline.yaml')