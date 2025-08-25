from flask import Flask, jsonify, request
from flask_cors import CORS
import servers_for_app 

app = Flask(__name__)
CORS(app)

@app.route('/execute', methods=['POST'])
def execute_commands():
    # request.get_json() 會取得前端傳來的 JSON 資料
    data = request.get_json()
    print("成功收到了來自前端的 POST 請求資料：", data)
    
    # 從收到的資料中取出伺服器資訊和指令
    host_data = data.get('host_data', '')
    command_data = data.get('command_data', '')
    result_data = servers_for_app.run(host_data, command_data)
    
    return jsonify({
        "status": result_data.get("status", "error"), 
        "output": result_data.get("report", "後端發生未知錯誤。") 
    })


if __name__ == '__main__':
    app.run(debug=True)