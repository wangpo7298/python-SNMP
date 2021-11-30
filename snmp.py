from pysnmp import hlapi


def constructObjectTypes(list_of_oids):
    """
    hlapi.getCmd need to certain type of object called hlapi.ObjectType
    so we will convert the all the oids to hlapi.ObjectType list.
    """
    return [hlapi.ObjectType(hlapi.ObjectIdentity(oid)) for oid in list_of_oids]


def convertDataType(data):
    """
    Here we need to convert the data we got from PySNMP to standard data type such as
    int, float, string.

    :param data: data from the PySNMP
    :return: data converted to standard data type
    """
    try:
        return int(data)
    except (ValueError, TypeError):
        try:
            return float(data)
        except (ValueError, TypeError):
            try:
                return str(data)
            except (ValueError, TypeError):
                pass
    return data


def fetch(hlr, count):
    result = list()
    for i in range(count):
        try:
            errIndication, errStatus, errorPos, varBinds = next(hlr)
            if not errIndication and not errStatus:
                items = {}
                for varBind in varBinds:
                    items[str(varBind[0])] = convertDataType(varBind[1])
                result.append(items)
            else:
                raise RuntimeError("Found SNMP Error: (0)".format(errIndication))
        except StopIteration:
            break
    return result


def constructMaptoPySNMPDataformat(pairValues):
    """
    this will convert the python dictionary to data accept by PySNMP
    :param pairValues: standard python map or dictionary
    :return:
    """
    values = []
    for key, value in pairValues.items():
        values.append(hlapi.ObjectType(hlapi.ObjectIdentity(key), value))
    return values


def get(target, listofOids, authData, port, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    """
    get is the snmp operation which will allows us to retrieve the data
    :param listofOids:
    :param target:  IP or name of the device
    :param oid: object identifier from MIB
    :param authData: credentials to authenticate
    :param port: not required but we can specify the UDP port
    :param engine: will be using SNMP engine which is heart of the SNMP protocol
    :return:
    """
    hlr = hlapi.getCmd(engine, authData, hlapi.UdpTransportTarget(target, port),
                       context, *constructObjectTypes(listofOids))
    return fetch(hlr, 1)[0]


def set(target, pairsValue, authData, port=143, engine=hlapi.SnmpEngine(),context=hlapi.ContextData()):
    hlr = hlapi.setCmd(engine, authData, hlapi.UdpTransportTarget((target, port)),
                       context, *constructMaptoPySNMPDataformat(pairsValue))
    return fetch(hlr, 1)[0]


print(get('10.0.0.1', ['1.3.5.3.0.6.1.2.0'], hlapi.CommunityData('CS158B')))

# return
# {'1.3.5.3.0.6.1.2.0': 'R1'}

set('10.0.0.1', {'1.3.5.3.0.6.1.2.0':'R1'}, hlapi.CommunityData('CS158B'))
