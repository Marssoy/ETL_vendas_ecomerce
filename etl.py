import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col

# Iniciar o contexto do Spark e Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# 1. Carregar os dados brutos do Glue Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="meu_catalogo",   # Substitua pelo nome do banco de dados no Glue Catalog
    table_name="vendas_csv"    # Substitua pelo nome da tabela no Glue Catalog
)

# 2. Converter o DynamicFrame para DataFrame
df = datasource.toDF()

# 3. Verificar as colunas do DataFrame
df.printSchema()  # Verifique o esquema das colunas carregadas
df.show(5)        # Visualize os primeiros 5 registros

# 4. Renomear a coluna correta (baseado no nome que você verificou)
# Supondo que "col4" seja o nome da coluna de Preço
df = df.withColumnRenamed("col4", "Preco")

# 5. Filtrar os dados para preços maiores que 0
df = df.filter(df["Preco"] > 0)

# 6. Criar a nova coluna "PrecoComDesconto" com 20% de desconto
df = df.withColumn("PrecoComDesconto", col("Preco") * 0.8)

# 7. Converter o DataFrame de volta para DynamicFrame
transformed_dynamic_frame = DynamicFrame.fromDF(df, glueContext, "transformed_data")

# 8. Definir o diretório de saída no S3
output_dir = "s3://marssoycloud.com.br/"  # Substitua pelo caminho do seu bucket no S3

# 9. Escrever os dados transformados no S3
glueContext.write_dynamic_frame.from_options(
    frame=transformed_dynamic_frame,  # DynamicFrame resultante das transformações
    connection_type="s3", 
    connection_options={"path": output_dir},
    format="csv"  # Formato do arquivo de saída
)