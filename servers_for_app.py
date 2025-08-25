import paramiko
import os


def run_file_commands(server,ssh_client,command_data,output_dir='server_outputs'):
    try:
        for i,command in enumerate(command_data.splitlines()):
            if not command:
                continue
            print(f"\n執行第 {i+1} 條指令：'{command}'...")
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            print(f"在伺服器 {server['hostname']} 執行的指令：'{command}'")
            output_file_name = f"{server['hostname']}_output{i+1}.txt"
            output_file_path = os.path.join(output_dir, output_file_name)
            write_output_to_file(server, command, output, error, output_file_path)
    except Exception as e:
        print(f"讀取檔案時發生錯誤：{e}")

def write_output_to_file(server, command, output, error, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(f"在伺服器 {server['hostname']} 執行的指令：'{command}'\n\n")
        if output:
            file.write("--- 輸出結果 ---\n")
            file.write(output)
        if error:
            file.write("\n--- 錯誤訊息 ---\n")
            file.write(error)
    print(f"結果已成功儲存到：{output_file_path}")
def input_serversfile(host_data):
    servers_info = []
    for line in host_data.strip().splitlines():
        if not line.strip(): 
            continue
        parts=line.strip().split(',')
        if len(parts)==3:
            server={
                'hostname':parts[0],
                'username':parts[1],
                'password':parts[2]
            }
            servers_info.append(server)
        else:
            print(f"檔案格式錯誤，應為 hostname,username,password 格式，但讀取到: {line}")
    return servers_info
def run(host_data,command_data):
    servers_info = input_serversfile(host_data)
    os.makedirs('server_outputs',exist_ok=True)
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
                print(f"連線成功！目前在伺服器：{server['hostname']}")
                run_file_commands(ssh_client,server,command_data)
        except paramiko.AuthenticationException:
            print(f"連線失敗：伺服器 {server['hostname']} 的帳號或密碼錯誤。")
        except Exception as e:
            print(f"連線到 {server['hostname']} 發生錯誤：{e}")
        finally:
            if 'ssh_client' in locals() and ssh_client:
                ssh_client.close()
                print("連線已關閉。")
    print("\n所有伺服器處理完畢！")
# def main():
#     host_data = 
# if __name__ == "__main__":
#     main()


