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

