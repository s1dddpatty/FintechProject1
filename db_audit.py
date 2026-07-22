from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("postgresql://fintech_user:fintech_secret@localhost:5432/fintech_analytics")

print("\n--- SECTION 2: DATABASE AUDIT ---")
with engine.connect() as conn:
    print("\nTable Sizes:")
    res = conn.execute(text('''
        SELECT relname as "Table",
               pg_size_pretty(pg_total_relation_size(relid)) As "Size",
               pg_stat_get_live_tuples(relid) as "Rows"
        FROM pg_catalog.pg_statio_user_tables 
        ORDER BY pg_total_relation_size(relid) DESC;
    '''))
    for row in res:
        print(row)

    print("\nIndexes:")
    res2 = conn.execute(text('''
        SELECT
            tablename,
            indexname,
            indexdef
        FROM
            pg_indexes
        WHERE
            schemaname = 'public'
        ORDER BY
            tablename,
            indexname;
    '''))
    for row in res2:
        print(row)

    print("\nMissing Indexes (Seq Scans > Index Scans):")
    res3 = conn.execute(text('''
        SELECT relname AS "Table",
               seq_scan AS "Seq Scans",
               idx_scan AS "Index Scans"
        FROM pg_stat_user_tables
        WHERE seq_scan > idx_scan
        ORDER BY seq_scan DESC;
    '''))
    for row in res3:
        print(row)
