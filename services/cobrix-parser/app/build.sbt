name := "cobrix-parser-service"
version := "1.0.0"
scalaVersion := "2.12.18"

// Spark dependencies (Cobrix will be provided via --jars at runtime)
val sparkVersion = "3.5.0"
libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql" % sparkVersion % "provided"
  // Note: Cobrix JAR will be provided via --jars in spark-submit
)

// Assembly plugin configuration
// Note: Plugin is loaded from project/plugins.sbt
import sbtassembly.AssemblyPlugin.autoImport._

assemblyJarName in assembly := "cobrix-parser-service.jar"
assemblyMergeStrategy in assembly := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}

