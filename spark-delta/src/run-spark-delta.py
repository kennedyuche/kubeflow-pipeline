from __future__ import print_function
import pyspark
import traceback
import configparser
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, LongType,  DateType
from pyspark.sql.functions import *
from delta import * 
from delta.tables import DeltaTable
import shutil
import configparser

import logging
logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)
logger.info("This is an INFO message on the root logger.")

config = configparser.ConfigParser()
config.read('config.cfg.template', encoding='utf-8-sig')

container_name       =  config['AZURE']['CONTAINER_NAME']
sink_container_name  =  config['AZURE']['SINK_CONTAINER_NAME']
storage_account_name =  config['AZURE']['STORAGE_ACCOUNT_NAME']
account_access_key   =  config['AZURE']['ACCOUNT_ACCESS_KEY']
sink_dir_name        =  config['AZURE']['SINK_DIRECTORY_NAME']

logger.info("Get storage name for table and raw data")
table_name             = config['STORAGE']['TABLE_NAME']
storage_dir_name       = config['STORAGE']['STORAGE_DIRECTORY_NAME']

logger.info("Delta table and storage data url")

AZURE_10K_CSV_DATA = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/{storage_dir_name}/*.csv"
DELTA_TABLE        = f"abfss://{sink_container_name}@{storage_account_name}.dfs.core.windows.net/{table_name}"


    
# load data from Azure Gen2
def session(spark):
    
    """
    ----------------------------
        Get the data schema
    ----------------------------
    :param name: string, name of the field. 
    :param dataType: :class:`DataType` of the field. 
    :param nullable: boolean, whether the field can be null (None) or not. 
    """
    logger.info("predefined schema of StrucType")
    docai_schema =  StructType(
                        [StructField("CIK", LongType(), True),
                        StructField("company_name", StringType(), True),
                        StructField("Items", StringType(), True),
                        StructField("Item Contents", StringType(), True),
                        StructField("file_url", StringType(), True)
                        ])
   

    logger.info("read csv dataframe from Azure")
#   logger.info(f"reading {Azure_10k_filings_data} filings data from azure storage : {storage_account_name}")
    logger.info(f"reading the filings data from azure storage : {storage_account_name}")

    df_filings = spark.read \
                      .format("csv") \
                      .option("header", "true") \
                      .option("inferSchema", "true") \
                      .option("nullValue", "null") \
                      .load(AZURE_10K_CSV_DATA)

    
    # If there is a need to specify the schema
#    df_filings = spark.read \
#                       .format("csv") \
#                       .option("header", "true") \
#                       .schema(docai_schema) \
#                       .load(AZURE_10K_CSV_DATA)
                       # .option("nullValue", "null")
                      
                      
    df_filings.show(15)
    
    
    """
    ----------------------------
        Write to a table
    ----------------------------
    """
    # Clear any previous runs
    logger.info("clearing any previous runs")
    shutil.rmtree(DELTA_TABLE, ignore_errors=True)
    
    # write to delta-lake
    # df_filings.write \
    #             .format("delta") \
    #             .save(DELTA_TABLE)
    # logger.info("Successfully written")
    # df_filings.show(truncate=False)
                                         
    logger.info("Atomically overwrite new data to an existing Delta table")
    logger.info(f"Overwrite data to the delta table : {table_name}")
    df_filings.write \
              .format("delta") \
              .mode("overwrite")  \
              .save(DELTA_TABLE)
             #.option("replaceWhere", "start_date >= '2017-01-01' AND end_date <= '2017-01-31'") \
    
    logger.info(f"Data stored to the Delta table {table_name}")


def readTable(spark):
    """
    ----------------------------------
        Read data from Delta table
    ----------------------------------

    """
    logger.info("sample data from the delta-table")
    table_data = spark.read \
                      .format("delta") \
                      .option("header", "true") \
                      .option("inferSchema", "true") \
                      .load(DELTA_TABLE)
                      
    return table_data.show(10)



if __name__ == "__main__":
    
    """
        Start Spark Session

    """

    try:
        builder = SparkSession.builder \
                .appName("Documentai") \
                .master("local[*]") \
                .config("spark.jars.packages", "io.delta:delta-core_2.12:1.1.0") \
                .config("spark.jars.packages", "org.apache.hadoop:hadoop-azure-datalake:3.3.1") \
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
                .config(f"spark.hadoop.fs.azure.account.auth.type.{storage_account_name}.dfs.core.windows.net", "SharedKey")\
                .config(f"spark.hadoop.fs.azure.account.key.{storage_account_name}.dfs.core.windows.net", f"{account_access_key}") 

        logger.info(SparkConf().getAll())
        spark = configure_spark_with_delta_pip(builder).getOrCreate()
        spark.sparkContext.setLogLevel('INFO')
        
    except Exception as error:
        logger.info(f"Exception occurred {error}")
        logger.info("Spark builder connection prompted out due to : %s", error)
        logger.info(traceback.format_exc())
        
    logger.info("instantiating the session to read data from Azure and write to delta-lake")
    session(spark)
    
    logger.info("Read and display few rows of data from delta-table")
    readTable(spark)
    
    logger.info("Stopping Spark session...")
    spark.stop()
