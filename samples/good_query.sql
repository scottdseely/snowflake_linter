-- Good SQL query with proper practices
select
    row_number() over (partition by customerid) as rn
from some_table;
