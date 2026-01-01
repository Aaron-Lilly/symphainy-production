#!/bin/bash
set -e

# Cobrix Spark Application entrypoint for stateless parsing
# Usage: parse.sh <input_file> <copybook_file> [output_dir]

INPUT_FILE=${1:-/input/data.bin}
COPYBOOK=${2:-/input/copybook.cpy}
OUTPUT_DIR=${3:-/output}

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Validate input files exist
if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE" >&2
    exit 1
fi

if [ ! -f "$COPYBOOK" ]; then
    echo "ERROR: Copybook file not found: $COPYBOOK" >&2
    exit 1
fi

# Export Spark home
export SPARK_HOME=/opt/cobrix/spark
export PATH=$SPARK_HOME/bin:$PATH

# Download Cobrix bundle JAR if not present (bundle includes all dependencies)
COBRIX_JAR="/tmp/cobrix-spark-cobol-bundle.jar"
if [ ! -f "$COBRIX_JAR" ]; then
    echo "Downloading Cobrix bundle JAR..."
    wget -q https://github.com/AbsaOSS/cobrix/releases/download/v2.9.0/spark-cobol_2.12-2.9.0-bundle.jar -O "$COBRIX_JAR" || \
    wget -q https://github.com/AbsaOSS/cobrix/releases/download/v2.8.4/spark-cobol_2.12-2.8.4-bundle.jar -O "$COBRIX_JAR" || {
        echo "ERROR: Failed to download Cobrix JAR" >&2
        exit 1
    }
fi

# Run our Spark application that uses Cobrix
# Provide Cobrix JAR via --jars
$SPARK_HOME/bin/spark-submit \
  --master local[1] \
  --jars "$COBRIX_JAR" \
  --class za.co.absa.cobrix.CobrixParserApp \
  --conf spark.sql.warehouse.dir=/tmp/spark-warehouse \
  --conf spark.driver.memory=2g \
  --conf spark.executor.memory=2g \
  --conf spark.driver.maxResultSize=2g \
  --conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
  /opt/cobrix/cobrix-parser-service.jar \
  --input "$INPUT_FILE" \
  --copybook "$COPYBOOK" \
  --output "$OUTPUT_DIR" \
  2>&1

# Check if output was created (Spark writes JSON files with part-XXXXX.json names)
OUTPUT_FILES=$(find "$OUTPUT_DIR" -name "part-*.json" 2>/dev/null | head -1)
if [ -n "$OUTPUT_FILES" ]; then
    echo "SUCCESS: Output files created in $OUTPUT_DIR"
    exit 0
else
    echo "ERROR: Output files not found in $OUTPUT_DIR" >&2
    exit 1
fi

