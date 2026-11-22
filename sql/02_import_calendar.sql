-- SignalSentinel AI
-- File: 02_import_calendar.sql
-- Purpose: Verify the calendar table before importing CSV data.

SELECT
column_name,
data_type,
is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'calendar'
ORDER BY ordinal_position;
