import logging
import uuid
from kubernetes import client, config

def get_k8s_api():
    config.load_incluster_config()
    api = client.CustomObjectsApi()
    return api

def create_sparkapplication(k8s_api):

  driver_pod_name = "docai-spark-app-" + str(uuid.uuid1())

  my_resource = {
    "apiVersion": "sparkoperator.k8s.io/v1beta2",
    "kind": "SparkApplication",
    "metadata": {
        "name": "driver_pod_name",
        "namespace": "kubeflow"
    },
    "spec": {
        "type": "Python",
        "pythonVersion": "3",
        "mode": "cluster",
        "image": "docaiacr.azurecr.io/spark-delta:v1",
        "imagePullPolicy": "Always",
        "mainApplicationFile": "local:///opt/app/spark_delta/run_spark_deltawriter.py",
        "sparkVersion": "3.1.1",
        "restartPolicy": {
            "type": "OnFailure",
            "onFailureRetries": 3,
            "onFailureRetryInterval": 10,
            "onSubmissionFailureRetries": 5,
            "onSubmissionFailureRetryInterval": 20
        },
        "driver": {
            "cores": 1,
            "coreLimit": "1200m",
            "memory": "512m",
            "labels": {
                "version": "3.1.1",
            },
            "serviceAccount": "spark-sa",
        },
        "executor": {
            "cores": 1,
            "instances": 1,
            "memory": "4084m",
            "labels": {
                "version": "3.1.1"
            }
        }
    }
}

  # create the resource
  k8s_api.create_namespaced_custom_object(
      group="sparkoperator.k8s.io",
      version="v1beta2",
      namespace="kubeflow",
      plural="sparkapplications",
      body=my_resource,
  )
  print("SparkApplication created")
  print("Spark Driver Pod Name: ", driver_pod_name+"-driver")

def main(argv=None):

  logging.getLogger().setLevel(logging.INFO)
  k8s_api = get_k8s_api()
  step_id = create_sparkapplication(k8s_api)

if __name__== "__main__":
  main()