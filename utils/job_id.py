import re

def remove_job_id_retry_suffix(task_id: str) -> str:
    # 正規表示式用於尋找 String 中的 "_retry"
    pattern = r'_retry$'
    
    # 將符合的結果用空字串取代
    result = re.sub(pattern, '', task_id)
    
    return result