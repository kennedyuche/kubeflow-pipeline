## Docai Kubeflow Pipeline Architecture  

## Kubeflow Components  
1. Data-loader component  
2. Spark-runner component  

## File Structure Overview  

```  
├── .github/workflows  
├── components  
|    ├── data-loader  
|    │   ├── src  
|    |   |   ├── util            
|    │   |   ├── download_10k_raw.py  
|    |   ├── dist  
|    |   |   ├── data_loader-1.0.0-py3-none-any.whl  
|    |   |   ├── data-loader-1.0.0.tar.gz  
|    |   ├── Dockerfile  
|    |   ├── entrypoint.sh  
|    |   ├── poetry.lock  
|    |   ├── pyproject.toml  
|    |   ├── README.md  
|    ├── spark-delta  
|    │   ├── src  
|    |   |   ├── util            
|    │   |   ├── run_spark_deltawriter.py  
|    |   ├── dist  
|    |   |   ├── spark_delta-1.0.0-py3-none-any.whl  
|    |   |   ├── spark_delta-1.0.0.tar.gz  
|    |   ├── Dockerfile  
|    |   ├── entrypoint.sh  
|    |   ├── poetry.lock  
|    |   ├── pyproject.toml  
|    |   ├── README.md  
|    ├── spark-job  
|    │   ├── spark_app.py  
|    │   ├── Dockerfile  
|    ├── kf-pipeline  
|    │   ├── data_loader_comp.yaml  
|    │   ├── spark_delta_comp.yaml  
|    │   ├── docai_pipeline.py  
|    │   ├── docai_pipeline.ipynb  
├─── deploy  
├─── gitignore  
├─── README.md  
├─── skaffold.yaml  
```

## Pipeline Architecture  
1. Data-Loader script and dependencies  
2. Spark-Delta script and dependencies  
3. Spark-Job configuration manifest  
4. Data-Loader component configuration files  
5. Spark-Delta component configuration files  
6. Kubeflow pipeline python compilation scripts  

### Data-Loader script and dependencies  
The data-loader script is configured, and a docker image is built for the data-loader. The image is used to configure the data-loader component of the kubeflow pipeline.  

### Spark-Delta script and dependencies  
The spark-delta script is configured, and a docker image is built for the spark-delta. The image is used to configure the spark-job (spark application) manifest.  

### Spark-Job configuration manifest  
A manifest file is configured to run the spark-delta job with spark operator. The image from spark-loader script is used for configuring the spark application manifest. A docker image is built for the spark-job, and the image is used for configuring the spark-delta component of the kubeflow pipeline.  

### Data-Loader pipeline component configuration  
The data-loader component of the pipeline is configured with the data-loader docker image. The configuration yaml file is as given below.

```  
name: data_loader
description: Download 10k files to Azure Datalake Storage

implementation:
  container:
    image: docaiacr.azurecr.io/data-loader:v1
    command: [ "/venv/bin/python3", "-m", "data_loader.download_10k_raw" ]
```  

The command activates the python virtual environment and runs the data-loader script.  

### Spark-Delta pipeline component configuration  
The spark-delta component of the pipeline component is configured with the spark-job docker image. The configuration yaml file is as given below.  

```  
name: Run Spark Job
description: Create docai spark app in the same k8s cluster for Spark-operator
implementation:
  container:
    image: docaiacr.azurecr.io/spark-job:v1
    command: ['python', 'create_spark_app.py']  
```  

### Kubeflow pipeline configuration  
The kubeflow components are compiled in a python script and notebook. 

```  
create_spark_app_op = load_component_from_file('spark_runner_comp.yaml')

create_data_loader_op = load_component_from_file('data_loader_comp.yaml')  

@dsl.pipeline(
    name='docai data pipeline',
    description='Load 10k files to Azure storage, run spark job to pick the data and load back to Azure Storage in delta format'
)
def docai_data_pipeline():
    step1 = create_data_loader_op()

    step2 = create_spark_app_op().after(step1)  

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(pipeline_func=docai_data_pipeline, package_path='docai_data_pipeline.yaml')
```  

The script will compile the pipeline and output a `yaml` file that will be uploaded to kubeflow for running the jobs.