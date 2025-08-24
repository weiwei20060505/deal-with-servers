import paramiko
import os


def input_servers():
    servers_info=[]
    while True:
        server={}
        server_name=input("請輸入伺服器名稱(不再輸入按n):")
        if server_name.lower()=='n':
            return servers_info
        server['hostname']=server_name
        server['username']=''
        server['password']=''
        # have_username=input("是否要改使用者名稱(y/n):")
        # if have_username.lower() == 'y'
        #     server['username']=input("請輸入使用者名稱:")
        # have_passward=input("是否要改密碼(y/n):")
        # if have_passward.lower() == 'y'
        #     server['passward']=input("請輸入密碼:")
        servers_info.append(server)
def get_and_run_server_commands(ssh_client,server,output_dir='server_outputs'):
    i=0
    while True:
        i+=1
        command=input(f"輸入第{i}條command(不再輸入按n):")
        if command.lower() == 'n':
            return 
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        print(f"在伺服器 {server['hostname']} 執行的指令：'{command}'")
        ifwrite=input("是否要將結果寫入檔案(y/n):")
        if ifwrite.lower() == 'y':
            output_file_name = f"{server['hostname']}_output{i}.txt"
            output_file_path = os.path.join(output_dir, output_file_name)
            write_output_to_file(server, command, output, error, output_file_path)
        
       
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
def input_serversfile():
    servers_info=[]
    file_path=input("請輸入伺服器檔案路徑(按y):")
    if file_path.lower() == 'y':
        file_path='host.txt'
    try:
        with open(file_path,'r') as file:
            lines=file.readlines()
            for line in lines:
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
    except FileNotFoundError:
        print(f"找不到檔案: {file_path}")
    return servers_info
def main():
    have_file=input("是否有伺服器檔案(y/n)")
    if have_file.lower() == 'y':
        servers_info = input_serversfile()
    else:
        servers_info = input_servers()
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
                get_and_run_server_commands(ssh_client,server)
        except paramiko.AuthenticationException:
            print(f"連線失敗：伺服器 {server['hostname']} 的帳號或密碼錯誤。")
        except Exception as e:
            print(f"連線到 {server['hostname']} 發生錯誤：{e}")
        finally:
            if 'ssh_client' in locals() and ssh_client:
                ssh_client.close()
                print("連線已關閉。")
    print("\n所有伺服器處理完畢！")
if __name__ == "__main__":
    main()


