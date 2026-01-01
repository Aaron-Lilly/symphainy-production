FROM eclipse-temurin:17-jdk as builder

ENV COBRIX_VERSION=2.8.0
ENV SPARK_VERSION=3.5.0
ENV SBT_VERSION=1.9.9

WORKDIR /opt/cobrix

# Install build tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install sbt (Scala Build Tool)
RUN wget -q https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}/sbt-${SBT_VERSION}.tgz && \
    tar -xzf sbt-${SBT_VERSION}.tgz && \
    rm sbt-${SBT_VERSION}.tgz

ENV PATH="/opt/cobrix/sbt/bin:${PATH}"

# Download Cobrix JAR directly from GitHub releases
RUN wget -q https://github.com/AbsaOSS/cobrix/releases/download/v2.9.3/spark-cobol_2.12-2.9.3.jar -O /tmp/cobrix.jar || \
    wget -q https://github.com/AbsaOSS/cobrix/releases/download/v2.8.0/spark-cobol_2.12-2.8.0.jar -O /tmp/cobrix.jar || \
    echo "Will download via --jars at runtime"

# Copy application source
COPY app/build.sbt /opt/cobrix/app/
COPY app/project /opt/cobrix/app/project/
COPY app/src /opt/cobrix/app/src/

# Build the Spark application (without Cobrix dependency - will use --jars)
WORKDIR /opt/cobrix/app
RUN sbt clean assembly || echo "Build will use --jars for Cobrix"

# Runtime stage
FROM eclipse-temurin:17-jre

ENV SPARK_VERSION=3.5.0
WORKDIR /opt/cobrix

# Install Python, pip, and dependencies for HTTP API
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for HTTP API
RUN pip3 install --no-cache-dir --break-system-packages fastapi uvicorn python-multipart

# Download Spark (required for running Spark applications)
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop3 spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

# Copy built JAR from builder stage
COPY --from=builder /opt/cobrix/app/target/scala-2.12/cobrix-parser-service.jar /opt/cobrix/cobrix-parser-service.jar

# Copy entrypoint script and HTTP API server
COPY app/parse.sh /usr/local/bin/parse.sh
COPY app/server.py /opt/cobrix/app/server.py
# Copy Python modules for copybook analysis and validation
COPY app/copybook_analyzer.py /opt/cobrix/app/copybook_analyzer.py
COPY app/cobol_metadata_validator.py /opt/cobrix/app/cobol_metadata_validator.py
COPY app/cobol_88_field_extractor.py /opt/cobrix/app/cobol_88_field_extractor.py
COPY app/file_format_normalizer.py /opt/cobrix/app/file_format_normalizer.py
RUN chmod +x /usr/local/bin/parse.sh
RUN chmod +x /opt/cobrix/app/server.py

# Expose port for HTTP API
EXPOSE 8080

# Start HTTP API server
CMD ["python3", "/opt/cobrix/app/server.py"]
