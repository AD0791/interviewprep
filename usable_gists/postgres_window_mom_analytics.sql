-- Use Case: Advanced Database Data Aggregations for Dashboards
-- Purpose: Prepares historical telemetry metrics, Month-over-Month (MoM) revenue changes, and rank orders.
-- Key features: CTEs, Window functions (SUM OVER), lagging values (LAG), and ranking (DENSE_RANK).

WITH daily_sales AS (
    -- Step 1: Bucket transactions by day and tenant
    SELECT 
        tenant_id,
        DATE_TRUNC('day', created_at) AS sales_date,
        SUM(amount) AS total_amount,
        COUNT(id) AS transaction_count
    FROM transactions
    WHERE status = 'completed'
    GROUP BY tenant_id, DATE_TRUNC('day', created_at)
),

sales_with_running_total AS (
    -- Step 2: Calculate running total in-place using WINDOW function
    SELECT 
        tenant_id,
        sales_date,
        total_amount,
        SUM(total_amount) OVER (
            PARTITION BY tenant_id 
            ORDER BY sales_date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_cumulative_sales
    FROM daily_sales
),

monthly_comparison AS (
    -- Step 3: Compute Month-over-Month changes using LAG
    SELECT 
        tenant_id,
        DATE_TRUNC('month', sales_date) AS sales_month,
        SUM(total_amount) AS monthly_revenue,
        LAG(SUM(total_amount), 1) OVER (
            PARTITION BY tenant_id 
            ORDER BY DATE_TRUNC('month', sales_date)
        ) AS previous_month_revenue
    FROM daily_sales
    GROUP BY tenant_id, DATE_TRUNC('month', sales_date)
)

-- Step 4: Final Selection and Rank Generation
SELECT 
    m.tenant_id,
    m.sales_month,
    m.monthly_revenue,
    m.previous_month_revenue,
    COALESCE(
        ((m.monthly_revenue - m.previous_month_revenue) / NULLIF(m.previous_month_revenue, 0)) * 100, 
        0
    ) AS mom_growth_percentage,
    DENSE_RANK() OVER (
        PARTITION BY m.sales_month 
        ORDER BY m.monthly_revenue DESC
    ) AS monthly_rank_in_platform
FROM monthly_comparison m
ORDER BY m.sales_month DESC, monthly_rank_in_platform ASC;
