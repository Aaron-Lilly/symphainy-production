package za.co.absa.cobrix

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

/**
 * Cobrix Parser Service - Spark Application
 * 
 * Parses COBOL mainframe files using Cobrix library.
 * 
 * Usage:
 *   spark-submit --class za.co.absa.cobrix.CobrixParserApp \
 *     cobrix-parser-service.jar \
 *     --input <input_file> \
 *     --copybook <copybook_file> \
 *     --output <output_dir>
 */
object CobrixParserApp {
  
  def main(args: Array[String]): Unit = {
    // Parse command line arguments
    val parsedArgs = parseArgs(args)
    
    val inputFile = parsedArgs.getOrElse("input", 
      throw new IllegalArgumentException("--input is required"))
    val copybookFile = parsedArgs.getOrElse("copybook",
      throw new IllegalArgumentException("--copybook is required"))
    val outputDir = parsedArgs.getOrElse("output",
      throw new IllegalArgumentException("--output is required"))
    val encoding = parsedArgs.getOrElse("encoding", "ascii") // Default to ASCII, can be "cp037", "cp1047", "ascii"
    
    // Create Spark session
    val spark = SparkSession.builder()
      .appName("CobrixParserService")
      .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
      .config("spark.driver.memory", "1g")
      .config("spark.executor.memory", "1g")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .getOrCreate()
    
    try {
      // Read COBOL file using Cobrix
      // Use file path method - the Python code already ensures the file is correctly formatted
      // The file has level numbers at column 0 (free-form format)
      
      System.err.println(s"DEBUG: Using copybook file path: $copybookFile")
      
      // Verify file exists and read first line for debugging
      val firstLine = scala.io.Source.fromFile(copybookFile, "UTF-8").getLines().take(1).mkString
      System.err.println(s"DEBUG: First line from file: $firstLine")
      System.err.println(s"DEBUG: First line length: ${firstLine.length}")
      System.err.println(s"DEBUG: First line bytes (hex): ${firstLine.getBytes("UTF-8").map(b => f"$b%02x").mkString}")
      if (firstLine.nonEmpty) {
        System.err.println(s"DEBUG: Char at position 0: '${firstLine(0)}' (${firstLine(0).toInt})")
        if (firstLine.length > 6) {
          System.err.println(s"DEBUG: Char at position 6: '${firstLine(6)}' (${firstLine(6).toInt})")
        }
      }
      
      System.err.println(s"DEBUG: Using encoding: $encoding")
      
      val df = spark.read
        .format("cobol")
        .option("copybook", copybookFile) // Use file path - Python code ensures correct format
        .option("schema_retention_policy", "keep_original")
        .option("encoding", encoding) // Use detected/configured encoding (ascii, cp037, cp1047)
        .option("record_format", "F") // Fixed-length records (replaces deprecated is_record_sequence)
        .option("copybook_paths", copybookFile) // Alternative option - might help with format detection
        .option("file_start_offset", 0) // Start reading from beginning (can be adjusted for headers)
        .option("file_trailer_length", 0) // No trailer expected
        // Note: Removed deprecated options: is_rdw_big_endian, is_rdw_part_of_record_length
        // Note: Cobrix will handle files that aren't perfectly divisible by warning and truncating
        .load(inputFile)
      
      // DEBUG: Print schema to see what fields Cobrix actually parsed
      System.err.println("DEBUG: Cobrix schema:")
      df.schema.foreach(field => {
        System.err.println(s"  Field: ${field.name}, Type: ${field.dataType}")
      })
      
      // Write as JSON (JSONL format - one JSON object per line)
      df.write
        .mode("overwrite")
        .option("compression", "none")
        .json(outputDir)
      
      println(s"SUCCESS: Parsed ${df.count()} records from $inputFile")
      println(s"Output written to: $outputDir")
      
    } catch {
      case e: Exception =>
        System.err.println(s"ERROR: Parsing failed: ${e.getMessage}")
        e.printStackTrace()
        System.exit(1)
    } finally {
      spark.stop()
    }
  }
  
  /**
   * Parse command line arguments into a map.
   * Expected format: --key value
   */
  def parseArgs(args: Array[String]): Map[String, String] = {
    args.sliding(2, 2).collect {
      case Array(key, value) if key.startsWith("--") =>
        key.substring(2) -> value
    }.toMap
  }
}

