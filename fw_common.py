def get_tag_value(object: dict):
    val = ""
    try:
        val = object["Tags"][0]["Value"]
    except KeyError:
        val = "none"
    except IndexError:
        val = "none"
    return val


def unify_state(state: str) -> str:
    ustate: str = state # unsupported states pass as-is
    # AWS state-s
    if state == "pending":
        ustate = "Running in progress"
    if state == "running":
        ustate = "Running"
    if state == "shutting-down":
        ustate = "Shutdown/Delete in progress"
    if state == "terminated":
        ustate = "Deleted"
    if state == "stopping":
        ustate = "Shutdown in progress"
    if state == "stopped":
        ustate = "Stoped"
    # Azure state-s
    #if state == "Provisioning succeeded":
    #    ustate = "Provisioning succeeded"
    #if state == "Provisioning failed":
    #    ustate = "Provisioning failed"
    if state == "Starting":
        ustate = "Running in progress"
    if state == "Running":
        ustate = "Running"
    if state == "Stopping":
        ustate = "Shutdown in progress"
    if state == "Stopped":
        ustate = "Stoped"
    if state == "Deallocating":
        ustate = "Shutdown/Delete in progress"
    if state == "Deallocated":
        ustate = "Stoped"
    if state == "Deleting":
        ustate = "Shutdown/Delete in progress"
    if state == "Deleted":
        ustate = "Deleted"
    if state == "VM deallocated":
        ustate = "Stoped"
    if state == "VM running":
        ustate = "Running"
    return ustate


def null_empty_str(str: str):
    val = str
    if str is None:
        val = None
    else:
        if str == '':
            val = None
    return val


def make_ports_string(str_from: str, str_to: str, proto: str):
    str1 = str2 = ""

    if str_from is None:
        str1 = "ALL"
    else:
        if f'{str_from}' == "-1" or f'{str_from}' == "":
            str1 = "ALL"
        else:
            str1 = f'{str_from}'

    if str_to is None:
        str2 = "ALL"
    else:
        if f'{str_to}' == "-1" or f'{str_to}' == "":
            str2 = "ALL"
        else:
            str2 = f'{str_to}'
    
    if proto.upper() == "ICMP":
        if str1 == '-1':
            str1 = 'Any'
        if str1 == '0':
            str1 = 'Any'
        if str1 == '*':
            str1 = 'Any'

        if str1 == 'Any':
            str2 = 'Any'
        else:
            if str2 == '-1':
                str2 = 'Any'
            if str2 == '0':
                str2 = 'Any'
            if str2 == '*':
                str2 = 'Any'
        ret = f'Type:{str1} Code:{str2}'
    else:
        if f'{str1}' == f'{str2}':
            ret = str1
        else:
            ret = f'{str1}-{str2}'
    return ret
