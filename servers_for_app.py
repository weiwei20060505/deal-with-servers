import paramiko
import os
from datetime import datetime
def run_file_commands(server, ssh_client, command_data):
    full_output = ""
    try:
        commands = [cmd.strip() for cmd in command_data.strip().splitlines() if cmd.strip()]
        for i, command in enumerate(commands):
            print(f"在 {server['hostname']} 上執行指令: '{command}'")
            stdin, stdout, stderr = ssh_client.exec_command(command)
            
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            full_output += f"$ {command}\n"
            if output:
                full_output += output
            if error:
                full_output += f"--- ERROR ---\n{error}"
            full_output += "\n"
    except Exception as e:
        error_msg = f"執行指令時發生錯誤：{e}\n"
        print(error_msg)
        full_output += error_msg
    
    return full_output

def input_serversfile(host_data):
    servers_info = []
    for line in host_data.strip().splitlines():
        if not line.strip(): 
            continue
        parts = line.strip().split(',')
        if len(parts) == 3:
            server = {
                'hostname': parts[0].strip(),
                'username': parts[1].strip(),
                'password': parts[2].strip()
            }
            servers_info.append(server)
        else:
            print(f"檔案格式錯誤，應為 hostname,username,password 格式，但讀取到: {line}")
    return servers_info

def run(host_data, command_data):
    servers_info = input_serversfile(host_data)
    if not servers_info:
        return {
            "status": "error",
            "report": "錯誤：沒有提供有效的伺服器資訊，或格式不符 (應為 hostname,username,password)。"
        }
    os.makedirs('server_outputs', exist_ok=True)
    # --- 【新增】建立一個帶有時間戳記的專屬資料夾 ---
    # 1. 取得當前時間
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # 2. 組合出資料夾名稱
    output_dir = f"server_outputs_{timestamp}"
    path = os.path.join('server_outputs', output_dir)
    # 3. 建立資料夾
    os.makedirs(path, exist_ok=True)
    print(f"所有伺服器的獨立紀錄檔將儲存於: {output_dir}")
    # --- 新增區塊結束 ---
    final_report = ""
    success_count = 0
    error_count = 0

    for server in servers_info:
        hostname = server['hostname']
        single_server_report = f"--- 開始處理伺服器: {hostname} ---\n"
        ssh_client = None
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            print(f"嘗試連線到伺服器: {hostname}...")
            ssh_client.connect(
                hostname=hostname,
                username=server['username'],
                password=server['password'],
                timeout=10
            )
            print(f"連線成功！目前在伺服器：{hostname}")
            
            result_output = run_file_commands(server, ssh_client, command_data)
            single_server_report += result_output
            
            success_count += 1
            single_server_report += f"--- 伺服器: {hostname} 處理完畢 ---\n\n"
            # --- 【新增】將這台伺服器的結果寫入獨立檔案 ---
            # 1. 建立一個安全的檔案名稱 (例如將 IP 中的 '.' 換成 '_')
            safe_filename = f"{hostname.replace('.', '_')}.txt"
            # 2. 組合出完整的檔案路徑
            file_path = os.path.join(path, safe_filename)
            # 3. 將報告寫入檔案，使用 utf-8 編碼
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(single_server_report)
            print(f"已將 {hostname} 的紀錄儲存至 {file_path}")
            # --- 新增區塊結束 ---
        except Exception as e:
            error_count += 1
            error_msg = f"!!! 處理伺服器 {hostname} 時發生嚴重錯誤: {str(e)}\n\n"
            print(error_msg)
            single_server_report += error_msg
        
        finally:
            if ssh_client:
                ssh_client.close()
                print(f"與 {hostname} 的連線已關閉。")
        final_report += single_server_report
    final_status = "success"
    if error_count > 0 and success_count > 0:
        final_status = "partial_success"
    elif error_count > 0 and success_count == 0:
        final_status = "error"
    summary = f"===== 批次任務總結 =====\n成功: {success_count} 台 | 失敗: {error_count} 台\n=========================\n\n"
    final_report = summary + final_report
    
    return {
        "status": final_status,
        "report": final_report
    }

