import os

KEYS = (
    'dd hh:mm:ss.mss', 'session_id', 'sql_text', 'login_name', 'wait_info',
    'CPU', 'tempdb_allocations', 'tempdb_current', 'blocking_session_id',
    'reads', 'writes', 'physical_reads', 'used_memory', 'status',
    'open_tran_count', 'percent_complete', 'host_name', 'database_name',
    'program_name', 'start_time', 'login_time', 'request_id',
    'collection_time',
)
LABELS = {
    'all': 'all queries to bill_ab',
    'pa': 'v_personal_account_vtb',
    'tbs': 'v_turnover_balance_sheet',
}
PATH = os.path.join('workload', 'logs')
