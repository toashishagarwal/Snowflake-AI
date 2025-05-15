-- Create a source table
CREATE TABLE source_table (id INT, name STRING, value INT);

-- Create a stream on the source table
CREATE STREAM source_stream ON TABLE source_table;

-- Create a target table for processed changes
CREATE TABLE target_table (
  id INT,
  name STRING, 
  value INT,
  change_type STRING,
  change_timestamp TIMESTAMP_NTZ
);

-- Create a task to process changes
CREATE TASK process_changes
  WAREHOUSE = compute_wh
  SCHEDULE = '1 minute'
AS
  INSERT INTO target_table
  SELECT 
    id, 
    name, 
    value,
    METADATA$ACTION,
    CURRENT_TIMESTAMP()
  FROM source_stream;
