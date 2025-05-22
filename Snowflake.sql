----------------------------------------
-- Show the roles assigned to a user
----------------------------------------
show grants to user AAGARWAL;

----------------------------------------
-- Use a given role
----------------------------------------
USE ROLE <rolename>;

----------------------------------------
-- Use all secondary roles assigned to a user
----------------------------------------
USE SECONDARY ROLES ALL;

----------------------------------------
-- To get a list of databases
----------------------------------------
SELECT * FROM information_schema.databases;

--------------------------------------------------------------
-- To get the clustering information of a table, column(s)
--------------------------------------------------------------
select system$clustering_information('ORDERS','(o_orderdate)');

--------------------------------------------------------------
-- Create DYNAMIC table
--------------------------------------------------------------
create dynamic table dt_sales_aggregate
target_lag   = "1 day"
warehouse    = sales_wh
refresh_mode = full
as
select s.sale_date,
       st.region
       sum(s.amount)
from sales s
join stores st
on   s.store_id = st.store_id;

-------------------------------------------------------------------
-- Create a STAGE
-------------------------------------------------------------------
Create or Replace Stage <STAGE_NAME>

-------------------------------------------------------------------
-- Add a file (models.zip) from local dir to STAGE-model_stage
-------------------------------------------------------------------
PUT file:///Users/aagarwal/Downloads/models.zip @model_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-------------------------------------------------------------------
-- List the files in STAGE-model_stage
-------------------------------------------------------------------
LIST @RESEARCH.AAGARWAL.model_stage

-------------------------------------------------------------------
-- Show all the stages
-------------------------------------------------------------------
SHOW stages;
       
-------------------------------------------------------------------
-- Check the currently Active behaviour change bundles
-------------------------------------------------------------------
SELECT SYSTEM$SHOW_ACTIVE_BEHAVIOR_CHANGE_BUNDLES();

-------------------------------------------------------------------
-- Create a new COMPUTE pool of GPUs for AI projects
-------------------------------------------------------------------
CREATE COMPUTE POOL tutorial_compute_pool
  MIN_NODES = 1
  MAX_NODES = 2
  INSTANCE_FAMILY = GPU_NV_S;

-------------------------------------------------------------------
-- Example of a HASH function
-------------------------------------------------------------------
SELECT MD5('Snowflake'), SHA2('Snowflake', 256);

-----------------------------------------------------------------------------------------
-- Example of a HASH_AGG function (Used on entire table to check data consistency)
-----------------------------------------------------------------------------------------
SELECT HASH_AGG(*) FROM mytable;

-----------------------------------------------------------------------------------------
-- Examples of Array transformations
-----------------------------------------------------------------------------------------
select **[1,2,3]; -- Gives 1,2,3 as columns

select greatest(**[11,2,3, 6]);  -- Gives the greatest element. 11 in this case
select coalesce(**[null,1,2,3]); -- 1 Returns the first non-NULL expression among its arguments, or NULL if all its arguments are NULL

select [**[1,2,3], **[4,5]]; -- Gives [1,2,3,4,5] combines the 2 arrays
select 1 col1 where col1 in (**[1,2,3], **[4,5]); -- Expand and combine arrays in where clauses. Gives 1 in this case

---------------------------------------------------------------------------------------------------------
-- Example of HLL function - Get an approximate count of distinct values
---------------------------------------------------------------------------------------------------------
SELECT HLL(email) from customers;        -- Takes 4x-5x less time but does not give exact cardinality
-- vs
SELECT COUNT(DISTINCT email) from customers; 

---------------------------------------------------------------------------------------------------------
-- Example of Alternative ways to query table without SELECT
---------------------------------------------------------------------------------------------------------
Table pune_customers;

Table pune_customers limit 2;

Table pune_customers BEFORE(OFFSET => -30)  -- Time travel queries

------------------------------------------------------------------------------------------------------------------
-- Example of JAROWINKLER_SIMILARITY
--       Computes the similarity between two input strings. The function returns an integer between 0 and 100, 
--       where 0 indicates no similarity and 100 indicates an exact match.
------------------------------------------------------------------------------------------------------------------
create or replace table st(s string, t string);
insert into st values('apple','apple');
insert into st values('apple','apple inc');
insert into st values('apple','apples');
insert into st values('big apple','apple');
insert into st values('apple','small apple');

table st;

select s,t, jarowinkler_similarity(s, t) from st;

------------------------------------------------------------------------------------------------------------------
-- Example of EDITDISTANCE 
--       Computes the Levenshtein distance between two input strings. It is the number of single-character 
--       insertions, deletions, or substitutions needed to convert one string to another. 
------------------------------------------------------------------------------------------------------------------
create or replace table st(s string, t string);
insert into st values('apple','apple');
insert into st values('apple','apple inc');
insert into st values('apple','apples');
insert into st values('big apple','apple');
insert into st values('apple','small apple');

table st;

select s,t, editdistance(s, t) from st;

-----------------------------------------------------------------------
-- Examples of FULL TEXT SEARCH 
------------------------------------------------------------------------
SELECT SEARCH('king','KING');  -- TRUE
SELECT SEARCH('5.1.33','32');  -- FALSE, since 32 is not there in param 1

SELECT SEARCH('King of Kalinga was Samrat Ashok','King and Queen'); -- TRUE, since one of 2nd param values is there in param 1. It defaults to OR

SELECT SEARCH('King of Kalinga was Samrat Ashok','King and Queen',SEARCH_MODE => 'AND'); -- FALSE, since we now forced to search using AND

-----------------------------------------------------------------------
-- Examples of FILTER over semi-structured JSON content
-- Filters people over 50 years of age
------------------------------------------------------------------------
SELECT FILTER(
  [
    {'name':'Patrick', 'age': 50},
    {'name':'Terry', 'age': 75},
    {'name':'Dyna', 'age': 25},
    {'name':'Ishwari', 'age': 32}
  ],
  a -> a:age >= 50) AS "People Over 50";

-----------------------------------------------------------------------------------
-- Example of FILTER over semi-structured JSON content
-- Filters people over 50 years of age
------------------------------------------------------------------------------------
SELECT TRANSFORM([5, 10, 15], a INT -> a / 5) AS "Divide by 5"; -- Gives [1, 2, 3]

SELECT TRANSFORM([5, 10, 3], a INT -> a / 5) AS "Divide by 5";  -- Gives [1, 2, 0.6]

-----------------------------------------------------------------------------------
-- Create a file format with options
-----------------------------------------------------------------------------------
CREATE OR REPLACE FILE FORMAT my_csv
  TYPE = CSV
  PARSE_HEADER = TRUE
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
  REPLACE_INVALID_CHARACTERS= TRUE
  SKIP_BLANK_LINES = TRUE;

-----------------------------------------------------------------------------------
-- Flow operator (aka Arrow operator) example
-----------------------------------------------------------------------------------
-- show specific cols from first sql query & order by specific col
show warehouses 
       ->> select "name", "state", "type", "size" from $1 order by "size";

-- Find research tables ending with _keep
show tables in database research 
       ->> select * from $1 where "name" ilike '%_keep';

-- Array of lowercase usersnames
show users 
       ->> select lower("name") as name from $1
              ->> select array_agg(name) from $1;

-- Get numeric column names from a table
describe table moa_live.stage.ABMD_DATA_REPORTED_20250515
       ->> select * from $1 where "type" ilike '%number%' 
              ->> select "name", "type" from $1;



