import subprocess
import pandas as pd

def get_chage_output(username):
    command = ['sudo', 'chage', '-l', username]
    chage_output = subprocess.check_output(command).decode()
    return chage_output.strip()  # Remove leading/trailing whitespace

def extract_values(chage_output):
    lines = chage_output.split('\n')
    values = [line.split(':', 1)[1].strip() for line in lines if ':' in line]
    return values

# Get hostname
host_check = ['hostname']
host_result = subprocess.check_output(host_check).decode("utf-8").strip()

data = []
with open('/etc/passwd', 'r') as passwd_file:
    for line in passwd_file:
        account = line.split(':')[0]
        chage_output = get_chage_output(account)
        values = extract_values(chage_output)
        last_pass_change, pass_expire, pass_inactive, acc_expire, mininum_number, maximum_number, warning = values[:7]
        data.append({'Hostname': host_result, 'Account Name': account, 'Last Password Change': last_pass_change, 'Password Expire': pass_expire, 'Password inactive': pass_inactive, 'Account expires': acc_expire, 'Minimum number of days between password change': mininum_number, 'Maximum number of days between password change': maximum_number, 'Number of days of warning before password expires': warning})

df = pd.DataFrame(data)
df.to_excel(f"{host_result}.output.xlsx", index=False)
