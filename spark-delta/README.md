spark for big data workloads

## instruction to run docker 


* Run `make build` to build the docker image with a tag

* After building the image, Run the built image and /bin/bash into the container
    * Run `make run` to run the built image

* The above command will open the container image, the directory were our application is copied to, you can run the sparkjob/main.py(testing) by running the command
    * Run `python3 main.py`

* In the `main.py` you can change the `container_name`, `storage_account_name`, `account_access_key` and the `table_name`(the name for your delta table) to your Azure account details.

* The `main.py` is for testing read/write to and from Azure Storage Gen 2, while the `spark_job.py` is our main application, which is still on hold until the new data schema is verified and pushed to the Storage Gen 2.



## Spark-job-cluster.yml file

- spark.kubernetes.authenticate.driver.serviceAccountName : Service account that is used when running the driver pod. The driver pod uses this service account when requesting executor pods from the API server. Note that this cannot be specified alongside a CA cert file, client key file, client cert file, and/or OAuth token. In client mode, use spark.kubernetes.authenticate.serviceAccountName instead.

- spark.kubernetes.authenticate.executor.serviceAccountName : Service account that is used when running the executor pod. If this parameter is not setup, the fallback logic will use the driver's service account.

- spark.kubernetes.executor.limit.cores : Specify a hard cpu limit for each executor pod launched for the Spark Application.

- spark.kubernetes.driver.limit.cores : Specify a hard cpu limit for the driver pod.

- spark.kubernetes.pyspark.pythonVersion : This sets the major Python version of the docker image used to run the driver and executor containers. It can be only "3". This configuration was deprecated from Spark 3.1.0, and is effectively no-op. Users should set 'spark.pyspark.python' and 'spark.pyspark.driver.python' configurations or 'PYSPARK_PYTHON' and 'PYSPARK_DRIVER_PYTHON' environment variables.

### Pod metadata key

- name : Value of spark.kubernetes.driver.pod.name : The driver pod name will be overwritten with either the configured or default value of spark.kubernetes.driver.pod.name. The executor pod names will be unaffected.

- namespace : Value of spark.kubernetes.namespace : Spark makes strong assumptions about the driver and executor namespaces. Both driver and executor namespaces will be replaced by either the configured or default spark conf value.


### Pod spec key

- restartPolicy : Spark assumes that both drivers and executors restarts on Failure.

- serviceAccount : Value of spark.kubernetes.authenticate.driver.serviceAccountName : Spark will override serviceAccount with the value of the spark configuration for only driver pods, and only if the spark configuration is specified. Executor pods will remain unaffected.


### Container spec key

- image : Value of spark.kubernetes.{driver,executor}.container.image : The image will be defined by the spark configurations.

- imagePullPolicy : Value of spark.kubernetes.container.image.pullPolicy : Spark will override the pull policy for both driver and executors.
