----------------------------------------
-- Show the roles assigned to a user
----------------------------------------
show grants to user AAGARWAL;

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



