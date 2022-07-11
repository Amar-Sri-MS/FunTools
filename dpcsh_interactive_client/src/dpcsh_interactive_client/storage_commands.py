from prettytable import PrettyTable, FRAME
from datetime import datetime
import time
import re
import json
from nu_commands import do_sleep_for_interval

VOL_TYPE_BLK_LOCAL_THIN = 'VOL_TYPE_BLK_LOCAL_THIN'
VOL_TYPE_BLK_RDS = 'VOL_TYPE_BLK_RDS'

class StorageCommands(object):
    def __init__(self, dpc_client):
        self.dpc_client = dpc_client

    def execute_commands(self, verb, command):
        try:
            if verb == "sdebug" or verb == "storage":
                 jsoncommand = json.loads(command)
                 result = self.dpc_client.execute(verb=verb, arg_list=[jsoncommand])
            else:
                result = self.dpc_client.execute(verb=verb, arg_list=[command])
            if result:
                print(json.dumps(result, indent=3))
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_controllers(self, grep=None):
        cmd = "storage/ctrlr/info/7/0"
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'controller uuid'])
                table_obj.align = 'l'
                counter = 0
                for key, val in result.iteritems():
                    for key, val in val.iteritems():
                        if key == "controller UUID":
                            counter += 1
                            table_obj.add_row([counter, val])
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_devices(self, grep=None):
        cmd = "storage/devices/nvme/ssds"
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'device_id'])
                table_obj.align = 'l' 
                counter = 0                                           
                for key, val in result.iteritems():
                    counter += 1
                    table_obj.add_row([counter, key])
                print table_obj
        except Exception as ex: 
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_volumes(self, voltype, jvol_uuid=None):
        cmd = "storage/volumes/"+voltype
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'volume uuid'])
                table_obj.align = 'l'
                counter = 0
                for key, val in result.iteritems():
                    if key == jvol_uuid:
                        counter += 1
                        table_obj.add_row([counter, key])
                    elif jvol_uuid == None:
                        counter += 1
                        table_obj.add_row([counter, key])
                print "******* %s ********" % voltype
                print table_obj
        except Exception as ex: 
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_volumes_pv(self, voltype):
        cmd = "storage/volumes/"+voltype
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'volume uuid', 'pvg_uuid', 'lsv_uuid'])
                table_obj.align = 'l'
                counter = 0
                for key, val in result.iteritems():
                    for ikey, ival in val.iteritems():
                        for inner_key in ival:
                            if inner_key == "pvg_uuid":
                                pvg_uuid = ival[inner_key]
                                pv_uuid = key
                                counter += 1
                    cmd1 = "storage/volumes/VOL_TYPE_BLK_PART_VG/%s" % pvg_uuid
                    result1 = self.dpc_client.execute(verb="peek", arg_list=[cmd1])
                    if result1:
                        for key, val in result1.iteritems():
                            for ikey in val:
                                if ikey == "md_vol_uuid":
                                    table_obj.add_row([counter, pv_uuid, pvg_uuid, val[ikey]])
                print "******* %s ********" % voltype
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_volumes_blt(self, voltype):
        cmd = "storage/volumes/"+voltype
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'volume uuid', 'drive_uuid', 'drive_id'])
                table_obj.align = 'l'
                counter = 0
                for key, val in result.iteritems():
                    if not key == 'drives' and not key == 'status':
                        drives = result['drives']
                        drive_uuid = None
                        drive_id = None
                        counter += 1
                        drive_uuid = val['stats']['drive_uuid']
                        drive_id = drives[drive_uuid]['drive_id']
                        table_obj.add_row([counter, key, drive_uuid, drive_id])
                print "******* %s ********" % voltype
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_volumes_rds(self, voltype):
        cmd = "storage/volumes/"+voltype
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'volume uuid', 'fabrics_info'])
                table_obj.align = 'l'
                counter = 0
                for key, val in result.iteritems():
                    counter += 1
                    info_obj = ""
                    for ikey, ival in val.iteritems():
                        for inner_key in ival:
                            if inner_key == "remote_ip" or inner_key == "remote_nsid" or inner_key == "remote_port" or inner_key == "remote_vol_type" or inner_key ==                              "subsys_nqn" or inner_key == "connections" or inner_key == "md_size" or inner_key == "ctrlr_id":
                                 info_obj = info_obj+str(inner_key)+":"+str(ival[inner_key])+"\n"
                    table_obj.add_row([counter, key, info_obj])
            print "******* %s ********" % voltype
            print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_volumes_replica(self, voltype, jvol_uuid=None, svol_uuid=None):
        cmd = "storage/volumes/"+voltype
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'volume uuid', 'nplexes', 'pvol-uuids'])
                table_obj.align = 'l'
                counter = 0
                num_replicas = None
                for key, val in result.iteritems():
                    if key == jvol_uuid or key == svol_uuid:
                        counter += 1
                        pinfo_obj = ""
                        num_replicas = val['stats']['num_replicas']
                        for ikey, ival in val.iteritems():
                            for inner_key in ival:
                                for x in range(0, num_replicas):
                                    if inner_key == "pvol" + str(x):
                                        pinfo_obj = pinfo_obj+str(inner_key)+":"+str(ival[inner_key])+"\n"
                        table_obj.add_row([counter, key, num_replicas, pinfo_obj])
			break
                    elif svol_uuid == None and  jvol_uuid == None:
                        counter += 1
                        pinfo_obj = ""
                        num_replicas = val['stats']['num_replicas']
                        for ikey, ival in val.iteritems():
                            for inner_key in ival:
                                for x in range(0, num_replicas):
                                    if inner_key == "pvol" + str(x):
                                        pinfo_obj = pinfo_obj+str(inner_key)+":"+str(ival[inner_key])+"\n"
                        table_obj.add_row([counter, key, num_replicas, pinfo_obj])
                print "******* %s ********" % voltype
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_volumes_ec(self, voltype, svol_uuid=None):
        cmd = "storage/volumes/"+voltype
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'volume uuid', 'nplexes', 'pvol-uuids'])
                table_obj.align = 'l'
                counter = 0
                for key, val in result.iteritems():
                    if key == svol_uuid:
                        counter += 1
                        pinfo_obj = ""
                        num_pvols = None
                        num_pvols = val['stats']['num_pvols']
                        for ikey, ival in val.iteritems():
                            for inner_key in ival:
                                for x in range(0, num_pvols):
                                    if inner_key == "pvol" + str(x):
                                        pinfo_obj = pinfo_obj+str(inner_key)+":"+str(ival[inner_key])+"\n"
                        break
                    elif svol_uuid == None:
                        counter += 1
                        pinfo_obj = ""
                        num_pvols = None
                        num_pvols = val['stats']['num_pvols']
                        for ikey, ival in val.iteritems():
                            for inner_key in ival:
                                for x in range(0, num_pvols):
                                    if inner_key == "pvol" + str(x):
                                        pinfo_obj = pinfo_obj+str(inner_key)+":"+str(ival[inner_key])+"\n"
                table_obj.add_row([counter, key, num_pvols, pinfo_obj])
                print "******* %s ********" % voltype
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_list_volumes_lsv(self, voltype):
        cmd = "storage/volumes/"+voltype
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                table_obj = PrettyTable(['sl no', 'volume uuid', 'svol_uuid', 'jvol_uuid'])
                table_obj.align = 'l'
                counter = 0
                for key, val in result.iteritems():
                    counter += 1
                    svol_uuid = None
                    jvol_uuid = None
                    for ikey, ival in val.iteritems():
                        for inner_key in ival:
                            if inner_key == "svol_uuid":
                                svol_uuid = str(ival[inner_key])
                            if inner_key == "jvol_uuid":
                                jvol_uuid = str(ival[inner_key])
                    table_obj.add_row([counter, key, svol_uuid, jvol_uuid])
                    self.storage_get_voltype(svol_uuid, jvol_uuid)
            print "******* %s ********" % voltype
            print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_get_voltype(self, svol_uuid, jvol_uuid):
        cmd = "storage/volumes"
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                for key, val, in result.iteritems():
                    for ikey, ival in val.iteritems():
                        if ikey == svol_uuid:
                            if key == 'VOL_TYPE_BLK_EC':
                                self.storage_list_volumes_ec(key, svol_uuid)
                            if key =='VOL_TYPE_BLK_REPLICA':
                                self.storage_list_volumes_replica(key, svol_uuid)
                        if ikey == jvol_uuid:
                            if key == 'VOL_TYPE_BLK_REPLICA':
                                self.storage_list_volumes_replica(key, jvol_uuid)
                            if key == 'VOL_TYPE_BLK_NV_MEMORY':
                                self.storage_list_volumes(key, jvol_uuid)
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_getsb_volume(self, vol_uuid, volume='volume', opcode='GET_SB'):
        try:
            params = {"vol_uuid":vol_uuid}
            cmd_arg_dict = {"params":params, "class":volume, "opcode":opcode}
            result = self.dpc_client.execute(verb="sdebug", arg_list=[cmd_arg_dict])
            if result:
                table_obj = PrettyTable()
                table_obj.align = 'l'
                for key, val in result.iteritems():
                    if key == "uuid":
                        table_obj.add_column("uuid", [val])
                    elif key == "voltype":
                        table_obj.add_column("voltype", [val])
                    elif key == "superblock":
                        str_obj = ""
                        for ikey in val:
                            str_obj = str_obj+str(ikey)+":"+str(val[ikey])+"\n"
                        table_obj.add_column("superblock", [str_obj], align='l')
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_getinfo_volume(self, vol_uuid, volume='volume', opcode='GET_INFO'):
        try:
            params = {"vol_uuid":vol_uuid}
            cmd_arg_dict = {"params":params, "class":volume, "opcode":opcode}
            result = self.dpc_client.execute(verb="sdebug", arg_list=[cmd_arg_dict])
            if result:
                table_obj = PrettyTable()
                table_obj.align = 'l'
                vp_obj = ""
                container_obj = ""
                lbs_obj = ""
                for key, val in result.iteritems():
                    if key == "uuid":
                        table_obj.add_column("vol_uuid", [val])
                    elif key == "voltype":
                        table_obj.add_column("vol_type", [val])
                    elif key == "vol_qos":
                        str_obj = ""
                        for ikey in val:
                            str_obj = str_obj+str(ikey)+": "+str(val[ikey])+"\n"
                        table_obj.add_column("vol_qos", [str_obj], align = 'l')
                    elif key == "large_block_store":
                        for ikey in val:
                            lbs_obj = lbs_obj+str(ikey)+": "+str(val[ikey])+"\n"
                    elif key == "lbs_id":
                        lbs_obj = lbs_obj+str(key)+": "+str(val)+"\n"
                    elif key == "vp" or key == "placement_cookie" or key == "done_vp":
                        vp_obj = vp_obj+str(key)+": "+str(val)+"\n"
                    else:
                        container_obj = container_obj+str(key)+": "+str(val)+"\n"
                table_obj.add_column("lbs_info", [lbs_obj], align = 'l')
                table_obj.add_column("vp_info", [vp_obj], align='l')
                table_obj.add_column("container_info", [container_obj], align = 'l')
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_getmap_volume(self, vol_uuid, slba, lbc, volume='volume', opcode='GET_MAP'):
        try:
            params = {"vol_uuid":vol_uuid, "slba":slba, "lbc":lbc}
            cmd_arg_dict = {"params":params, "class":volume, "opcode":opcode}
            result = self.dpc_client.execute(verb="sdebug", arg_list=[cmd_arg_dict])
            if result:
                table_obj = PrettyTable()
                table_obj.align = 'l'
                table1_obj = PrettyTable(['slba', 'pba_info'])
                table1_obj.align = 'l'
                for key, val in result.iteritems():
                    if key == "vol_uuid":
                        table_obj.add_column("vol_uuid", [val])
                    elif key == "drive_id":
                        table_obj.add_column("drive_id", [val])
                    elif key == "lbs":
                        table_obj.add_column("lbs", [val])
                    elif key == "container_id":
                        table_obj.add_column("container_id", [val])
                    else:
                        pba_obj = ""
                        for ikey in val:
                            pba_obj = pba_obj+str(ikey)+":"+str(val[ikey])+"\n"
                        table1_obj.add_row([key, pba_obj])
                print table_obj
                print table1_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_controller_stats(self, ctrlr_uuid):
        cmd = "storage/ctrlr/info/7/0"
        storagepeekcommands = StoragePeekCommands(self.dpc_client)
        try:
            prev_result = None
            while True:
                try:
                    result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
                    if result:
                        if prev_result:
                            diff_result = storagepeekcommands._get_difference(result=result, prev_result=prev_result)
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter', 'Counter Diff'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    if result[key][_key] == ctrlr_uuid:
                                        for _key in sorted(result[key]):
                                            if _key == "name_spaces":
                                                continue
                                            else:
                                                table_obj.add_row([_key, result[key][_key], diff_result[key][_key]])
                                        print table_obj
                                        prev_result = result[key]
                        else:
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    if result[key][_key] == ctrlr_uuid:
                                        for _key in sorted(result[key]):
                                            if _key == "name_spaces":
                                                continue
                                            else:
                                                table_obj.add_row([_key, result[key][_key]])
                                        print table_obj
                                        prev_result = result[key]
                        print "\n########################  %s ########################\n" % str(storagepeekcommands._get_timestamp())
                        do_sleep_for_interval()
                except KeyboardInterrupt:
                    self.dpc_client.disconnect()
                    break
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_volume_stats(self, vol_uuid, voltype):
        cmd = "storage/volumes/%s/%s" % (voltype, vol_uuid)
        storagepeekcommands = StoragePeekCommands(self.dpc_client)
        try:
            prev_result = None
            while True:
                try:
                    result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
                    result.pop('controller', None)
                    master_table_obj = PrettyTable()
                    master_table_obj.align = 'l'
                    master_table_obj.header = False
                    if result:
                        if prev_result:
                            diff_result = storagepeekcommands._get_difference(result=result, prev_result=prev_result)
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter', 'Counter Diff'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    table_obj.add_row([_key, result[key][_key], diff_result[key][_key]])
                                master_table_obj.add_row([key, table_obj])
                        else:
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    table_obj.add_row([_key, result[key][_key]])
                                master_table_obj.add_row([key, table_obj])
                        prev_result = result
                        print master_table_obj
                        print "\n########################  %s ########################\n" % str(storagepeekcommands._get_timestamp())
                        do_sleep_for_interval()
                    else:
                        print "Empty result"

                except KeyboardInterrupt:
                    self.dpc_client.disconnect()
                    break
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def storage_device_stats(self, device_id):
       cmd = "storage/devices/nvme/ssds"
       storagepeekcommands = StoragePeekCommands(self.dpc_client)
       try:
           prev_result = None
           while True:
               try:
                   result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
                   if result:
                       if prev_result:
                           diff_result = storagepeekcommands._get_difference(result=result, prev_result=prev_result)
                           for key in sorted(result):
                               table_obj = PrettyTable(['Field Name', 'Counter', 'Counter Diff'])
                               table_obj.align = 'l'
                               table_obj.sortby = 'Field Name'
                               if key == device_id:
                                   for _key in sorted(result[key]):
                                       table_obj.add_row([_key, result[key][_key], diff_result[key][_key]])
			           print table_obj
                       else:
                           for key in sorted(result):
                               table_obj = PrettyTable(['Field Name', 'Counter'])
                               table_obj.align = 'l'
                               table_obj.sortby = 'Field Name'
                               if key == device_id:
                                   for _key in sorted(result[key]):
                                       table_obj.add_row([_key, result[key][_key]])
			           print table_obj
                       prev_result = result
                       print "\n########################  %s ########################\n" % str(storagepeekcommands._get_timestamp())
                       do_sleep_for_interval()
                   else:
                       print "Empty result"
                       break
               except KeyboardInterrupt:
                   self.dpc_client.disconnect()
                   break
       except Exception as ex:
           print "ERROR: %s" % str(ex)
           self.dpc_client.disconnect()

    def storage_rdsock_vp_stats(self, controller='controller', opcode='GET_RDSOCK_VP_STATS'):
        try:
            cmd_arg_dict = {"class":controller, "opcode":opcode}
            result = self.dpc_client.execute(verb="sdebug", arg_list=[cmd_arg_dict])
            if result:
                table_obj = PrettyTable(['vp', 'rdsock info'])
                table_obj.align = 'l'
                for key, val in result.iteritems():
                    rdsock_obj = ""
                    for ikey, ival in val.iteritems():
                        if ikey == "instances":
                            rdsock_obj = rdsock_obj+str(ikey)+":"+"\n"
                            for inner_key in ival:
                                rdsock_obj = rdsock_obj+str(inner_key)+":"+str(ival[inner_key])+"\n"
                        if ikey == "stats_client" or ikey == "stats_server":
                            rdsock_obj =  rdsock_obj+str(ikey)+":"+"\n"
                            for inner_key in ival:
                                rdsock_obj = rdsock_obj+str(inner_key)+":"+str(ival[inner_key])+"\n"
                    table_obj.add_row([key, rdsock_obj])
                print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

class StoragePeekCommands(object):
    def __init__(self, dpc_client):
        self.dpc_client = dpc_client

    def _get_timestamp(self):
        ts = time.time()
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

    def _get_difference(self, result, prev_result):
        """
        :param result: Should be dict or dict of dict
        :param prev_result: Should be dict or dict of dict
        :return: dict or dict of dict
        """
        diff_result = {}
        for key in result:
            if type(result[key]) == dict:
                diff_result[key] = {}
                for _key in result[key]:
                    if key in prev_result and _key in prev_result[key]:
                        if type(result[key][_key]) == dict:
                            diff_result[key][_key] = {}
                            for inner_key in result[key][_key]:
                                if inner_key in prev_result[key][_key]:
                                    if type(result[key][_key][inner_key]) == unicode:
                                        diff_result[key][_key][inner_key] = result[key][_key][inner_key]
                                    else:
                                        diff_value = result[key][_key][inner_key] - prev_result[key][_key][inner_key]
                                        diff_result[key][_key][inner_key] = diff_value
                                else:
                                    diff_result[key][_key][inner_key] = 0
                        else:
                            if type(result[key][_key]) == unicode:
                                diff_result[key][_key] = result[key][_key]
                            else:
                                diff_value = result[key][_key] - prev_result[key][_key]
                                diff_result[key][_key] = diff_value
                    else:
                        diff_result[key][_key] = 0
            elif type(result[key]) == str:
                diff_result[key] = result[key]
            else:
                if key in prev_result:
                    if type(result[key]) == list:
                        diff_result[key] = result[key]
                        continue
                    diff_value = result[key] - prev_result[key]
                    diff_result[key] = diff_value
                else:
                    diff_result[key] = result[key]

        return diff_result

    def _get_required_ssd_results(self, result, ssd_ids):
        output = {}
        not_found_list = []
        for ssd_id in ssd_ids:
            if ssd_id not in result.keys():
                not_found_list.append(ssd_id)
            else:
                output[ssd_id] = result[ssd_id]
        if not_found_list:
            str1 = ' '.join(not_found_list)
            print "SSDs with ids %s not found" % str1
        return output


    def peek_connected_ssds(self, ssd_ids=[], grep=None):
        try:
            prev_result = None
            while True:
                try:
                    cmd = "storage/devices/nvme/ssds"
                    result = self.dpc_client.execute(verb="peek", arg_list=[cmd], tid=4)
                    for drive in result:
                        del result[drive]['nguid']
                    master_table_obj = PrettyTable()
                    master_table_obj.align = 'l'
                    master_table_obj.header = False
                    if ssd_ids:
                        result = self._get_required_ssd_results(result, ssd_ids)
                    if result:
                        if prev_result:
                            diff_result = self._get_difference(result=result, prev_result=prev_result)
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter', 'Counter Diff'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    if grep:
                                        if re.search(grep, _key, re.IGNORECASE):
                                            table_obj.add_row([_key, result[key][_key], diff_result[key][_key]])
                                    else:
                                        table_obj.add_row([_key, result[key][_key], diff_result[key][_key]])

                                else:
                                    master_table_obj.add_row([key, table_obj])
                        else:
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    if grep:
                                        if re.search(grep, _key, re.IGNORECASE):
                                            table_obj.add_row([_key, result[key][_key]])
                                    else:
                                        table_obj.add_row([_key, result[key][_key]])
                                else:
                                    master_table_obj.add_row([key, table_obj])
                        prev_result = result
                        print master_table_obj
                        print "\n########################  %s ########################\n" % str(self._get_timestamp())
                        do_sleep_for_interval()
                    else:
                        print "Empty result"
                        break
                except KeyboardInterrupt:
                    self.dpc_client.disconnect()
                    break
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def _peek_vol_stats(self, cmd):
        try:
            prev_result = None
            while True:
                try:
                    result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
                    master_table_obj = PrettyTable()
                    master_table_obj.align = 'l'
                    master_table_obj.header = False
                    if result:
                        if prev_result:
                            diff_result = self._get_difference(result=result, prev_result=prev_result)
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter', 'Counter Diff'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    table_obj.add_row([_key, result[key][_key], diff_result[key][_key]])
                                master_table_obj.add_row([key, table_obj])
                        else:
                            for key in sorted(result):
                                table_obj = PrettyTable(['Field Name', 'Counter'])
                                table_obj.align = 'l'
                                table_obj.sortby = 'Field Name'
                                for _key in sorted(result[key]):
                                    table_obj.add_row([_key, result[key][_key]])
                                master_table_obj.add_row([key, table_obj])
                        prev_result = result
                        print master_table_obj
                        print "\n########################  %s ########################\n" % str(self._get_timestamp())
                        do_sleep_for_interval()
                    else:
                        print "Empty result"

                except KeyboardInterrupt:
                    self.dpc_client.disconnect()
                    break
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()

    def peek_blt_vol_stats(self, vol_id):
        cmd = "storage/volumes/%s/%s" % (VOL_TYPE_BLK_LOCAL_THIN, vol_id)
        self._peek_vol_stats(cmd=cmd)

    def peek_rds_vol_stats(self, vol_id):
        cmd = "storage/volumes/%s/%s" % (VOL_TYPE_BLK_RDS, vol_id)
        self._peek_vol_stats(cmd=cmd)

    def peek_storage_volumes(self, grep=None):
        cmd = "storage/volumes"
        try:
            result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
            if result:
                for key, val in result.iteritems():
                    if key == VOL_TYPE_BLK_RDS:
                        table_obj = PrettyTable(['sl no', 'volume uuid'])
                        table_obj.align = 'l'
                        counter = 0
                        for vol in val.keys():
                            counter += 1
                            table_obj.add_row([counter, vol])
                        print "******* %s ********" % key
                        print table_obj
                    if key == VOL_TYPE_BLK_LOCAL_THIN:
                        drives = result[VOL_TYPE_BLK_LOCAL_THIN]['drives']
                        table_obj = PrettyTable(['sl no', 'volume_uuid', 'drive_uuid', 'drive_id'])
                        table_obj.align = 'l'
                        counter = 0
                        print_table = False
                        for vol in val.keys():
                            if not vol == 'drives' and not vol == 'status':
                                drive_uuid = None
                                drive_id = None
                                counter += 1
                                drive_uuid = val[vol]['stats']['drive_uuid']
                                drive_id = drives[drive_uuid]['drive_id']
                                table_obj.add_row([counter, vol, drive_uuid, drive_id])
                                print_table = True
                        if print_table:
                            print "******* %s ********" % key
                            print table_obj
        except Exception as ex:
            print "ERROR: %s" % str(ex)
            self.dpc_client.disconnect()
