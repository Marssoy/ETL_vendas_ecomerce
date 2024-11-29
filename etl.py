import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame  # Import necessário para trabalhar com DynamicFrame
from pyspark.sql.functions import col, round  # Import para trabalhar com colunas e arredondamento

# Iniciar o contexto do Spark e Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# 1. Carregar os dados brutos do Glue Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="nome_do_seu_catalogo",   # Substitua pelo nome do banco de dados no Glue Catalog
    table_name="nome_da_sua_tabela"    # Substitua pelo nome da tabela no Glue Catalog
)

# 2. Converter o DynamicFrame para DataFrame para realizar transformações
df = datasource.toDF()

# 3. Realizar a transformação no DataFrame
# Filtrar apenas produtos com preços maiores que 0
df = df.filter(df["Preco"] > 0)

# Criar uma nova coluna com 20% de desconto no preço, arredondando para 2 casas decimais
df = df.withColumn("PrecoComDesconto", round(col("Preco") * 0.8, 2))

# 4. Converter o DataFrame de volta para DynamicFrame
transformed_dynamic_frame = DynamicFrame.fromDF(df, glueContext, "transformed_data")

# 5. Definir o diretório de saída no S3
output_dir = "s3://seu_bucket/"  # Substitua pelo caminho do seu bucket no S3

# 6. Escrever os dados transformados no S3
glueContext.write_dynamic_frame.from_options(
    frame=transformed_dynamic_frame,  # DynamicFrame resultante das transformações
    connection_type="s3", 
    connection_options={"path": output_dir},
    format="csv"  # Formato do arquivo de saída
)
