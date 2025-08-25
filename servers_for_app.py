import paramiko
import os

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
   
    final_report = ""
    success_count = 0
    error_count = 0

    for server in servers_info:
        hostname = server['hostname']
        final_report += f"--- 開始處理伺服器: {hostname} ---\n"
        
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
            final_report += result_output
            
            success_count += 1
            final_report += f"--- 伺服器: {hostname} 處理完畢 ---\n\n"

        except Exception as e:
            error_count += 1
            error_msg = f"!!! 處理伺服器 {hostname} 時發生嚴重錯誤: {str(e)}\n\n"
            print(error_msg)
            final_report += error_msg
        
        finally:
            if ssh_client:
                ssh_client.close()
                print(f"與 {hostname} 的連線已關閉。")
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

