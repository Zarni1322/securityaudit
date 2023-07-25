import pandas as pd
import paramiko

def establish_ssh_connection(hostname, username, password):
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    client.connect(hostname, username=username, password=password)

    return client

def close_ssh_connection(client):
    if client:
        client.close()

def get_user_accounts(client):
    # Read the list of user accounts from /etc/passwd
    _, stdout, _ = client.exec_command('cut -d: -f1 /etc/passwd')
    accounts = stdout.read().decode().splitlines()
    return accounts

def get_chage_output(client, account):
    # Use sudo only for the chage command
    command = f'sudo chage -l {account}'
    _, stdout, _ = client.exec_command(command)
    chage_output = stdout.read().decode()
    return chage_output.strip()  # Remove leading/trailing whitespace

def extract_values(chage_output):
    if not chage_output:
        # Return default values if the output is empty
        return ["N/A"] * 7

    lines = chage_output.split('\n')
    values = [line.split(':', 1)[1].strip() for line in lines if ':' in line]
    
    if len(values) < 7:
        # If there are not enough values, pad with default values
        values.extend(["N/A"] * (7 - len(values)))

    return values

def main():
    # SSH Connection details
    remote_hostname = '172.16.16.6'
    remote_username = 'root'
    remote_password = 'toor'

    # Establish the SSH connection
    ssh_client = establish_ssh_connection(remote_hostname, remote_username, remote_password)

    try:
        # Get hostname
        host_check = ['hostname']
        _, stdout, _ = ssh_client.exec_command('hostname')
        host_result = stdout.read().decode().strip()

        # Get user accounts
        user_accounts = get_user_accounts(ssh_client)

        data = []
        for account in user_accounts:
            chage_output = get_chage_output(ssh_client, account)
            values = extract_values(chage_output)
            last_pass_change, pass_expire, pass_inactive, acc_expire, mininum_number, maximum_number, warning = values[:7]

            data.append({#'Hostname': host_result,
                        'IP Address': remote_hostname,
                         'Username': account,
                         'Last Password Change': last_pass_change,
                         'Password Expire': pass_expire,
                         'Password inactive': pass_inactive,
                         'Account expires': acc_expire,
                         'Minimum number of days': mininum_number,
                         'Maximum number of days': maximum_number,
                         'Number of days of warning before password expires': warning})

        df = pd.DataFrame(data)
        df.to_excel(f"{remote_hostname}.xlsx", index=False)

    finally:
        # Close the SSH connection when done
        close_ssh_connection(ssh_client)

if __name__ == "__main__":
    main()
