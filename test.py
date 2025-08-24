import paramiko
import os

servers_info = [
    {
        'hostname': 'localhost',
        'username': 'weiwei',
        'password': '8ss#(4yJ_d8BHEW',
        'command': 'whoami'  
    },

]

output_dir = 'server_outputs'
os.makedirs(output_dir, exist_ok=True)

for server in servers_info:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"嘗試連線到伺服器: {server['hostname']}...")
    
    try:
        ssh_client.connect(
            hostname=server['hostname'],
            username=server['username'],
            password=server['password']
        )
        print(f"連線成功！正在執行指令：'{server['command']}'")

        # 執行遠端指令，會回傳三個標準串流（輸入、輸出、錯誤）
        stdin, stdout, stderr = ssh_client.exec_command(server['command'])
        
        # 讀取標準輸出和標準錯誤的內容，並解碼成文字
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        output_file_name = f"{server['hostname']}_output.txt"
        output_file_path = os.path.join(output_dir, output_file_name)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(f"在伺服器 {server['hostname']} 執行的指令：'{server['command']}'\n\n")
            if output:
                file.write("--- 輸出結果 ---\n")
                file.write(output)
            if error:
                file.write("\n--- 錯誤訊息 ---\n")
                file.write(error)
        
        print(f"結果已成功儲存到：{output_file_path}")

    except paramiko.AuthenticationException:
        print(f"連線失敗：伺服器 {server['hostname']} 的帳號或密碼錯誤。")
    except Exception as e:
        print(f"連線到 {server['hostname']} 發生錯誤：{e}")
    finally:
        if 'ssh_client' in locals() and ssh_client:
            ssh_client.close()
            print("連線已關閉。")

print("\n所有伺服器處理完畢！")
