#使用 DHT sensor library 中範例 DHTtest
#需確認 DHT11 腳位插接正確
import serial  # 引用pySerial模組
import time
import requests
Token = 'ENTER YOUR LINE NOTIFY TOKEN HERE'
#GET LINE NOTIFY TOKEN : https://www.youtube.com/watch?v=QX1p4kWkFQg

T_TH = 29.5 #溫度警示上限  
H_TH = 90 #溼度警示上限

def lineNotifyMessage(token, msg):
    print("line message:"+msg)
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)

State = [0]
def notifyMachine(T,H,token=Token):
    if State[0] == 0: #'nomal'
        if T>T_TH :
            lineNotifyMessage(Token,"[warning]溫度超過"+str(T_TH)+"度")
            State[0] = 1 #'abnomal'
        if H>H_TH :
            lineNotifyMessage(Token,"[warning]溼度超過"+str(H_TH)+"%")
            #print('[warning]溼度超過'+str(H_TH)+"%")
            State[0] = 1 #'abnomal'
    else:
        if T<T_TH and H<H_TH :
            State[0] += 1
            if State[0] > 8:
                State[0] =0
                lineNotifyMessage(Token,'溫度溼度恢復正常')
        else:State[0]=1
                
def findSerial(msg,BAUD_RATES=9600,checkStart=3,checkEnd=32):
    for i in range(checkStart,checkEnd+1):
        try:
            ser = serial.Serial("COM"+str(i), BAUD_RATES)   # 初始化序列通訊埠
            while True:
                while ser.in_waiting:          # 若收到序列資料…
                    data = ser.readline().decode()   # 用預設的UTF-8解碼
                    if msg in data:
                        print(data)
                        return ser
        except serial.SerialException: pass
        except KeyboardInterrupt: 
            print('breaking from user')
            ser.close();return None
        

ser = findSerial(msg="%")
if ser != None: print('connect successfully')
    
filename = "DHT%Y%m%d%H.txt"
f = open(time.strftime(filename),'w')
reopenN = 5
i = 0
try:
    while True:
        time.sleep(0.5)
        if ser == None:print("can't any detect serial");break
        while ser.in_waiting:          
            data = time.strftime("%H:%M:%S\t") + ser.readline().decode().strip() # 讀取一行
            print(data)
            f.write(data+'\n')
            i = (i + 1) % reopenN
            if i == 0 : f.close() ; f = open(filename,'a')
                
            if filename != time.strftime("DHT%Y%m%d%H.txt"):
                f.close();f = open(time.strftime("DHT%Y%m%d%H.txt"),'w')              
            filename = time.strftime("DHT%Y%m%d%H.txt")
            
            T = float(data.split()[2][0:-2].strip())
            H = float(data.split()[1][0:-1].strip())
            print(T,H)
            notifyMachine(T,H)
            
except KeyboardInterrupt:ser.close()    # 清除序列通訊物件
#except : print("不正常中斷")
print('serial closed')
