from dpc_shell import DpcShell
from dpc_client import DpcClient
from cmd2 import Cmd, with_argparser
from nu_commands import *
from funos_commands import *
from storage_commands import *
from cmd_arg_parser import *
import sys


class CmdController(Cmd):

    def __init__(self, target_ip, target_port, verbose=False):
        Cmd.__init__(self)
        self.prompt = "(dpc_cli) "
        self.dpc_client = DpcClient(target_ip=target_ip, target_port=target_port, verbose=verbose)
        self._port_cmd_obj = PortCommands(dpc_client=self.dpc_client)
        self._funos_cmd_obj = FunOSCommands(dpc_client=self.dpc_client)
        self._sys_cmd_obj = SystemCommands(dpc_client=self.dpc_client)
        self._qos_cmd_obj = QosCommands(dpc_client=self.dpc_client)
        self._peek_cmd_obj = PeekCommands(dpc_client=self.dpc_client)
        self._clear_cmd_obj = NuClearCommands(dpc_client=self.dpc_client)
        self._sample_cmd_obj = SampleCommands(dpc_client=self.dpc_client)
        self._show_cmd_obj = ShowCommands(dpc_client=self.dpc_client)
        self._meter_cmd_obj = MeterCommands(dpc_client=self.dpc_client)
        self._flow_cmd_obj = FlowCommands(dpc_client=self.dpc_client)
        self._debug_cmd_obj = DebugCommands(dpc_client=self.dpc_client)
        self._storage_peek_obj = StoragePeekCommands(dpc_client=self.dpc_client)
        self._storage_obj = StorageCommands(dpc_client=self.dpc_client)
        self._execute_obj = StorageCommands(dpc_client=self.dpc_client)

    def check_cluster_id_range(self, cluster_id):
        result = True
        if not ((int(cluster_id) <= 8) and (int(cluster_id) >= 0)):
            print "Enter cluster id between 0 and 7. You entered %s" % cluster_id
            result = False
        return result

    def check_core_id_range(self, core_id):
        result = True
        if not ((core_id <= 5) and (core_id >= 0)):
            print "Enter core id between 0 and 5. You entered %s" % core_id
            result = False
        return result

    def set_system_time_interval(self, args):
        time_interval = args.time
        self._sys_cmd_obj.time_interval(time_interval=time_interval)

    def get_system_time_interval(self, args):
        self._sys_cmd_obj.time_interval(time_interval=None)

    def set_port_mtu(self, args):
        port_num = args.port_num
        shape = args.shape
        mtu_value = args.mtu_value
        self._port_cmd_obj.port_mtu(port_num=port_num, shape=shape, mtu=mtu_value)

    def get_port_mtu(self, args):
        port_num = args.port_num
        shape = args.shape
        self._port_cmd_obj.port_mtu(port_num=port_num, shape=shape)

    def get_sdn_flow_layers(self, args):
        self._peek_cmd_obj.get_sdn_flow_layers()

    def set_nu_meter(self, args):
        index = args.index
        interval = args.interval
        crd = args.crd
        commit_rate = args.commit_rate
        pps_mode = args.pps_mode
        excess_rate = args.excess_rate
        commit_burst = args.commit_burst
        excess_burst = args.excess_burst
        direction = args.direction
        len_mode = args.len_mode
        rate_mode = args.rate_mode
        color_aware = args.color_aware
        unit = args.unit
        rsvd = args.rsvd
        len8 = args.len8
        common = args.common
        bank = args.bank
        self._meter_cmd_obj.set_meter(index=index, interval=interval, crd=crd, commit_rate=commit_rate,
                                      pps_mode=pps_mode, excess_rate=excess_rate, commit_burst=commit_burst,
                                      excess_burst=excess_burst, direction=direction, len_mode=len_mode,
                                      rate_mode=rate_mode, color_aware=color_aware, unit=unit, rsvd=rsvd, len8=len8,
                                      common=common, bank=bank)

    def enable_port(self, args):
        self._port_cmd_obj.enable_disable_port(port_num=args.port_num, shape=args.shape)

    def disable_port(self, args):
        self._port_cmd_obj.enable_disable_port(port_num=args.port_num, shape=args.shape, enable=False)

    def enable_port_link_pause(self, args):
        self._port_cmd_obj.enable_disable_link_pause(port_num=args.port_num, shape=args.shape)

    def disable_port_link_pause(self, args):
        self._port_cmd_obj.enable_disable_link_pause(port_num=args.port_num, shape=args.shape, enable=False)

    def enable_port_tx_link_pause(self, args):
        self._port_cmd_obj.enable_disable_tx_link_pause(port_num=args.port_num, shape=args.shape)

    def disable_port_tx_link_pause(self, args):
        self._port_cmd_obj.enable_disable_tx_link_pause(port_num=args.port_num, shape=args.shape, enable=False)

    def set_port_pause_quanta(self, args):
        self._port_cmd_obj.port_pause_quanta(port_num=args.port_num, shape=args.shape, quanta=args.quanta)

    def get_port_pause_quanta(self, args):
        self._port_cmd_obj.port_pause_quanta(port_num=args.port_num, shape=args.shape)

    def get_port_link_status(self, args):
        self._port_cmd_obj.port_link_status()

    def set_port_pause_threshold(self, args):
        self._port_cmd_obj.port_pause_threshold(port_num=args.port_num, shape=args.shape, threshold=args.threshold)

    def get_port_pause_threshold(self, args):
        self._port_cmd_obj.port_pause_threshold(port_num=args.port_num, shape=args.shape)

    def enable_port_pfc(self, args):
        self._port_cmd_obj.enable_disable_pfc(port_num=args.port_num, shape=args.shape)

    def disable_port_pfc(self, args):
        self._port_cmd_obj.enable_disable_pfc(port_num=args.port_num, shape=args.shape, enable=False)

    def enable_port_tx_pfc(self, args):
        self._port_cmd_obj.enable_disable_tx_pfc(port_num=args.port_num, shape=args.shape, class_num=args.class_num)

    def disable_port_tx_pfc(self, args):
        self._port_cmd_obj.enable_disable_tx_pfc(port_num=args.port_num, shape=args.shape, enable=False,
                                                 class_num=args.class_num)

    def set_port_pfc_quanta(self, args):
        self._port_cmd_obj.port_pfc_quanta(port_num=args.port_num, shape=args.shape, quanta=args.quanta,
                                           class_num=args.class_num)

    def get_port_pfc_quanta(self, args):
        self._port_cmd_obj.port_pfc_quanta(port_num=args.port_num, shape=args.shape, class_num=args.class_num)

    def set_port_pfc_threshold(self, args):
        self._port_cmd_obj.port_pfc_threshold(port_num=args.port_num, shape=args.shape, threshold=args.threshold,
                                              class_num=args.class_num)

    def get_port_pfc_threshold(self, args):
        self._port_cmd_obj.port_pfc_threshold(port_num=args.port_num, shape=args.shape, class_num=args.class_num)

    def enable_port_ptp_peer_delay(self, args):
        self._port_cmd_obj.enable_disable_ptp_peer_delay(port_num=args.port_num, shape=args.shape)

    def disable_port_ptp_peer_delay(self, args):
        self._port_cmd_obj.enable_disable_ptp_peer_delay(port_num=args.port_num, shape=args.shape, enable=False)

    def set_port_ptp_peer_delay(self, args):
        self._port_cmd_obj.ptp_peer_delay(port_num=args.port_num, shape=args.shape, delay=args.delay)

    def get_port_ptp_peer_delay(self, args):
        self._port_cmd_obj.ptp_peer_delay(port_num=args.port_num, shape=args.shape)

    def get_port_ptp_tx_ts(self, args):
        self._port_cmd_obj.get_ptp_tx_ts(port_num=args.port_num, shape=args.shape)

    def enable_port_ptp_1step(self, args):
        self._port_cmd_obj.enable_disable_ptp_1step(port_num=args.port_num, shape=args.shape)

    def disable_port_ptp_1step(self, args):
        self._port_cmd_obj.enable_disable_ptp_1step(port_num=args.port_num, shape=args.shape, enable=False)

    def set_port_runt_filter(self, args):
        self._port_cmd_obj.set_runt_filter(port_num=args.port_num, shape=args.shape, buffer=args.buffer_64,
                                           runt_err_en=args.runt_err_en, en_delete=args.en_delete)

    def dump_port_runt_filter(self, args):
        self._port_cmd_obj.dump_runt_filter(port_num=args.port_num, shape=args.shape)

    def set_system_syslog_level(self, args):
        self._sys_cmd_obj.system_syslog_level(level_val=args.level_val)

    def get_system_syslog_level(self, args):
        self._sys_cmd_obj.system_syslog_level(level_val=None)

    def set_qos_egress_buffer_pool(self, args):
        sf_thr = args.sf_thr
        sx_thr = args.sx_thr
        df_thr = args.df_thr
        dx_thr = args.dx_thr
        fcp_thr = args.fcp_thr
        nonfcp_thr = args.nonfcp_thr
        sample_copy_thr = args.sample_copy_thr
        sf_xoff_thr = args.sf_xoff_thr
        sf_xon_thr = args.sf_xon_thr
        fcp_xoff_thr = args.fcp_xoff_thr
        nonfcp_xoff_thr = args.nonfcp_xoff_thr
        self._qos_cmd_obj.egress_buffer_pool(sf_thr=sf_thr, sx_thr=sx_thr, df_thr=df_thr, dx_thr=dx_thr,
                                             fcp_thr=fcp_thr, nonfcp_xoff_thr=nonfcp_xoff_thr,
                                             sample_copy_thr=sample_copy_thr, nonfcp_thr=nonfcp_thr,
                                             fcp_xoff_thr=fcp_xoff_thr, sf_xoff_thr=sf_xoff_thr, sf_xon_thr=sf_xon_thr,update_config=True)

    def set_hnu_qos_egress_buffer_pool(self, args):
        sf_thr = args.sf_thr
        sx_thr = args.sx_thr
        df_thr = args.df_thr
        dx_thr = args.dx_thr
        fcp_thr = args.fcp_thr
        nonfcp_thr = args.nonfcp_thr
        sample_copy_thr = args.sample_copy_thr
        sf_xoff_thr = args.sf_xoff_thr
        fcp_xoff_thr = args.fcp_xoff_thr
        nonfcp_xoff_thr = args.nonfcp_xoff_thr
        self._qos_cmd_obj.egress_buffer_pool(sf_thr=sf_thr, sx_thr=sx_thr, df_thr=df_thr, dx_thr=dx_thr,
                                             fcp_thr=fcp_thr, nonfcp_xoff_thr=nonfcp_xoff_thr,
                                             sample_copy_thr=sample_copy_thr, nonfcp_thr=nonfcp_thr,
                                             fcp_xoff_thr=fcp_xoff_thr, sf_xoff_thr=sf_xoff_thr, update_config=True,
                                             mode='hnu')

    def get_qos_egress_buffer_pool(self, args):
        self._qos_cmd_obj.egress_buffer_pool(update_config=False)

    def get_hnu_qos_egress_buffer_pool(self, args):
        self._qos_cmd_obj.egress_buffer_pool(update_config=False, mode='hnu')

    def set_qos_egress_port_buffer(self, args):
        port_num = args.port_num
        min_thr = args.min_thr
        shared_thr = args.shared_thr
        self._qos_cmd_obj.egress_port_buffer(port_num=port_num, min_thr=min_thr, shared_thr=shared_thr)

    def set_hnu_qos_egress_port_buffer(self, args):
        port_num = args.port_num
        min_thr = args.min_thr
        shared_thr = args.shared_thr
        self._qos_cmd_obj.egress_port_buffer(port_num=port_num, min_thr=min_thr, shared_thr=shared_thr, mode='hnu')

    def get_qos_egress_port_buffer(self, args):
        port_num = args.port_num
        self._qos_cmd_obj.egress_port_buffer(port_num=port_num, update_config=False)

    def get_hnu_qos_egress_port_buffer(self, args):
        port_num = args.port_num
        self._qos_cmd_obj.egress_port_buffer(port_num=port_num, update_config=False, mode='hnu')

    def set_qos_egress_queue_buffer(self, args):
        port_num = args.port_num
        queue = args.queue
        min_thr = args.min_thr
        static_shared_thr_green = args.static_shared_thr_green
        dynamic_enable = args.dynamic_enable
        shared_thr_alpha = args.shared_thr_alpha
        shared_thr_offset_yellow = args.shared_thr_offset_yellow
        shared_thr_offset_red = args.shared_thr_offset_red
        self._qos_cmd_obj.egress_queue_buffer(port_num=port_num, queue=queue,
                                              min_thr=min_thr, static_shared_thr_green=static_shared_thr_green,
                                              shared_thr_alpha=shared_thr_alpha, dynamic_enable=dynamic_enable,
                                              shared_thr_offset_red=shared_thr_offset_red,
                                              shared_thr_offset_yellow=shared_thr_offset_yellow)

    def set_hnu_qos_egress_queue_buffer(self, args):
        port_num = args.port_num
        queue = args.queue
        min_thr = args.min_thr
        static_shared_thr_green = args.static_shared_thr_green
        dynamic_enable = args.dynamic_enable
        shared_thr_alpha = args.shared_thr_alpha
        shared_thr_offset_yellow = args.shared_thr_offset_yellow
        shared_thr_offset_red = args.shared_thr_offset_red
        self._qos_cmd_obj.egress_queue_buffer(port_num=port_num, queue=queue,
                                              min_thr=min_thr, static_shared_thr_green=static_shared_thr_green,
                                              shared_thr_alpha=shared_thr_alpha, dynamic_enable=dynamic_enable,
                                              shared_thr_offset_red=shared_thr_offset_red,
                                              shared_thr_offset_yellow=shared_thr_offset_yellow, mode='hnu')

    def get_qos_egress_queue_buffer(self, args):
        port_num = args.port_num
        queue = args.queue
        self._qos_cmd_obj.egress_queue_buffer(port_num=port_num, update_config=False, queue=queue)

    def get_hnu_qos_egress_queue_buffer(self, args):
        port_num = args.port_num
        queue = args.queue
        self._qos_cmd_obj.egress_queue_buffer(port_num=port_num, update_config=False, queue=queue, mode='hnu')

    def set_qos_egress_priority_map(self, args):
        port_num = args.port_num
        map_list = args.map_list
        self._qos_cmd_obj.egress_queue_to_priority_map(port_num=port_num, map_list=map_list, update=True)

    def set_hnu_qos_egress_priority_map(self, args):
        port_num = args.port_num
        map_list = args.map_list
        self._qos_cmd_obj.egress_queue_to_priority_map(port_num=port_num, map_list=map_list, update=True)

    def get_qos_egress_priority_map(self, args):
        port_num = args.port_num
        self._qos_cmd_obj.egress_queue_to_priority_map(port_num=port_num, update=False)

    def get_hnu_qos_egress_priority_map(self, args):
        port_num = args.port_num
        self._qos_cmd_obj.egress_queue_to_priority_map(port_num=port_num, update=False, mode='hnu')

    def set_qos_ecn_glb_sh_threshold(self, args):
        en = args.en
        green = args.green
        red = args.red
        yellow = args.yellow
        self._qos_cmd_obj.ecn_glb_sh_threshold(en=en, green=green, red=red, yellow=yellow, update=True)

    def set_hnu_qos_ecn_glb_sh_threshold(self, args):
        en = args.en
        green = args.green
        red = args.red
        yellow = args.yellow
        self._qos_cmd_obj.ecn_glb_sh_threshold(en=en, green=green, red=red, yellow=yellow, update=True, mode='hnu')

    def get_qos_ecn_glb_sh_threshold(self, args):
        self._qos_cmd_obj.ecn_glb_sh_threshold(update=False)

    def get_hnu_qos_ecn_glb_sh_threshold(self, args):
        self._qos_cmd_obj.ecn_glb_sh_threshold(update=False, mode='hnu')

    def set_qos_ecn_profile(self, args):
        prof_num = args.prof_num
        min_thr = args.min_thr
        max_thr = args.max_thr
        ecn_prob_index = args.ecn_prob_index
        self._qos_cmd_obj.ecn_profile(prof_num=prof_num, min_thr=min_thr, max_thr=max_thr,
                                      ecn_prob_index=ecn_prob_index, update=True)

    def set_hnu_qos_ecn_profile(self, args):
        prof_num = args.prof_num
        min_thr = args.min_thr
        max_thr = args.max_thr
        ecn_prob_index = args.ecn_prob_index
        self._qos_cmd_obj.ecn_profile(prof_num=prof_num, min_thr=min_thr, max_thr=max_thr,
                                      ecn_prob_index=ecn_prob_index, update=True, mode='hnu')

    def get_qos_ecn_profile(self, args):
        prof_num = args.prof_num
        self._qos_cmd_obj.ecn_profile(prof_num=prof_num, update=False)

    def get_hnu_qos_ecn_profile(self, args):
        prof_num = args.prof_num
        self._qos_cmd_obj.ecn_profile(prof_num=prof_num, update=False, mode='hnu')

    def set_qos_ecn_prob(self, args):
        prob_idx = args.prob_idx
        prob = args.prob
        self._qos_cmd_obj.ecn_prob(prob=prob, prob_idx=prob_idx, update=True)

    def set_hnu_qos_ecn_prob(self, args):
        prob_idx = args.prob_idx
        prob = args.prob
        self._qos_cmd_obj.ecn_prob(prob=prob, prob_idx=prob_idx, update=True, mode='hnu')

    def get_qos_ecn_prob(self, args):
        prob_idx = args.prob_idx
        self._qos_cmd_obj.ecn_prob(prob_idx=prob_idx, update=False)

    def get_hnu_qos_ecn_prob(self, args):
        prob_idx = args.prob_idx
        self._qos_cmd_obj.ecn_prob(prob_idx=prob_idx, update=False,mode='hnu')

    def set_qos_wred_profile(self, args):
        prof_num = args.prof_num
        min_thr = args.min_thr
        max_thr = args.max_thr
        wred_prob_index = args.wred_prob_index
        self._qos_cmd_obj.wred_profile(prof_num=prof_num, min_thr=min_thr, max_thr=max_thr,
                                       wred_prob_index=wred_prob_index, update=True)

    def set_hnu_qos_wred_profile(self, args):
        prof_num = args.prof_num
        min_thr = args.min_thr
        max_thr = args.max_thr
        wred_prob_index = args.wred_prob_index
        self._qos_cmd_obj.wred_profile(prof_num=prof_num, min_thr=min_thr, max_thr=max_thr,
                                       wred_prob_index=wred_prob_index, update=True, mode='hnu')

    def get_qos_wred_profile(self, args):
        prof_num = args.prof_num
        self._qos_cmd_obj.wred_profile(prof_num=prof_num, update=False)

    def get_hnu_qos_wred_profile(self, args):
        prof_num = args.prof_num
        self._qos_cmd_obj.wred_profile(prof_num=prof_num, update=False, mode='hnu')

    def set_qos_wred_prob(self, args):
        prob_idx = args.prob_idx
        prob = args.prob
        self._qos_cmd_obj.wred_prob(prob=prob, prob_idx=prob_idx, update=True)

    def set_hnu_qos_wred_prob(self, args):
        prob_idx = args.prob_idx
        prob = args.prob
        self._qos_cmd_obj.wred_prob(prob=prob, prob_idx=prob_idx, update=True, mode='hnu')

    def get_qos_wred_prob(self, args):
        prob_idx = args.prob_idx
        self._qos_cmd_obj.wred_prob(prob_idx=prob_idx, update=False)

    def get_hnu_qos_wred_prob(self, args):
        prob_idx = args.prob_idx
        self._qos_cmd_obj.wred_prob(prob_idx=prob_idx, update=False, mode='hnu')

    def set_qos_wred_queue_config(self, args):
        port_num = args.port_num
        queue_num = args.queue
        wred_en = args.wred_en
        wred_weight = args.wred_weight
        wred_prof_num = args.wred_prof_num
        ecn_en = args.ecn_en
        ecn_prof_num = args.ecn_prof_num
        self._qos_cmd_obj.wred_queue_config(port_num=port_num, queue_num=queue_num, wred_en=wred_en,
                                            wred_weight=wred_weight, wred_prof_num=wred_prof_num, ecn_en=ecn_en,
                                            ecn_prof_num=ecn_prof_num, update=True)

    def set_hnu_qos_wred_queue_config(self, args):
        port_num = args.port_num
        queue_num = args.queue
        wred_en = args.wred_en
        wred_weight = args.wred_weight
        wred_prof_num = args.wred_prof_num
        ecn_en = args.ecn_en
        ecn_prof_num = args.ecn_prof_num
        self._qos_cmd_obj.wred_queue_config(port_num=port_num, queue_num=queue_num, wred_en=wred_en,
                                            wred_weight=wred_weight, wred_prof_num=wred_prof_num, ecn_en=ecn_en,
                                            ecn_prof_num=ecn_prof_num, update=True, mode='hnu')

    def get_qos_wred_queue_config(self, args):
        port_num = args.port_num
        queue_num = args.queue
        self._qos_cmd_obj.wred_queue_config(port_num=port_num, queue_num=queue_num, update=False)

    def get_hnu_qos_wred_queue_config(self, args):
        port_num = args.port_num
        queue_num = args.queue
        self._qos_cmd_obj.wred_queue_config(port_num=port_num, queue_num=queue_num, update=False, mode='hnu')

    def set_qos_wred_avg_q_config(self, args):
        q_avg_en = args.q_avg_en
        cap_avg_sz = args.cap_avg_sz
        avg_period = args.avg_period
        self._qos_cmd_obj.wred_avg_q_config(q_avg_en=q_avg_en, cap_avg_sz=cap_avg_sz, avg_period=avg_period,
                                            update=True)

    def set_hnu_qos_wred_avg_q_config(self, args):
        q_avg_en = args.q_avg_en
        cap_avg_sz = args.cap_avg_sz
        avg_period = args.avg_period
        self._qos_cmd_obj.wred_avg_q_config(q_avg_en=q_avg_en, cap_avg_sz=cap_avg_sz, avg_period=avg_period,
                                            update=True, mode='hnu')

    def get_qos_wred_avg_q_config(self, args):
        self._qos_cmd_obj.wred_avg_q_config(update=False)

    def get_hnu_qos_wred_avg_q_config(self, args):
        self._qos_cmd_obj.wred_avg_q_config(update=False, mode='hnu')

    def get_qos_scheduler_config(self, args):
        port_num = args.port_num
        queue = args.queue
        self._qos_cmd_obj.get_scheduler_config(port_num=port_num, queue_num=queue)

    def get_hnu_qos_scheduler_config(self, args):
        port_num = args.port_num
        queue = args.queue
        self._qos_cmd_obj.get_scheduler_config(port_num=port_num, queue_num=queue, mode='hnu')

    def set_qos_scheduler_config_dwrr(self, args):
        port_num = args.port_num
        queue = args.queue
        weight = args.weight
        self._qos_cmd_obj.scheduler_config_dwrr(port_num=port_num, queue_num=queue, weight=weight)

    def set_hnu_qos_scheduler_config_dwrr(self, args):
        port_num = args.port_num
        queue = args.queue
        weight = args.weight
        self._qos_cmd_obj.scheduler_config_dwrr(port_num=port_num, queue_num=queue, weight=weight, mode='hnu')

    def set_qos_scheduler_config_shaper(self, args):
        port_num = args.port_num
        queue = args.queue
        shaper_enable = args.enable
        shaper_type = args.type
        shaper_rate = args.rate
        shaper_threshold = args.thresh
        self._qos_cmd_obj.scheduler_config_shaper(port_num=port_num, queue_num=queue,
                                                  shaper_enable=shaper_enable,
                                                  shaper_type=shaper_type,
                                                  shaper_rate=shaper_rate,
                                                  shaper_threshold=shaper_threshold)

    def set_hnu_qos_scheduler_config_shaper(self, args):
        port_num = args.port_num
        queue = args.queue
        shaper_enable = args.enable
        shaper_type = args.type
        shaper_rate = args.rate
        shaper_threshold = args.thresh
        self._qos_cmd_obj.scheduler_config_shaper(port_num=port_num, queue_num=queue,
                                                  shaper_enable=shaper_enable,
                                                  shaper_type=shaper_type,
                                                  shaper_rate=shaper_rate,
                                                  shaper_threshold=shaper_threshold, mode='hnu')

    def set_qos_scheduler_config_strict_priority(self, args):
        port_num = args.port_num
        queue = args.queue
        strict_priority_enable = args.strict_priority_enable
        extra_bandwidth = args.extra_bandwidth
        self._qos_cmd_obj.scheduler_config_strict_priority(port_num=port_num, queue_num=queue,
                                                           strict_priority_enable=strict_priority_enable,
                                                           extra_bandwidth=extra_bandwidth)

    def set_hnu_qos_scheduler_config_strict_priority(self, args):
        port_num = args.port_num
        queue = args.queue
        strict_priority_enable = args.strict_priority_enable
        extra_bandwidth = args.extra_bandwidth
        self._qos_cmd_obj.scheduler_config_strict_priority(port_num=port_num, queue_num=queue,
                                                           strict_priority_enable=strict_priority_enable,
                                                           extra_bandwidth=extra_bandwidth, mode='hnu')

    def set_qos_ingress_pg(self, args):
        port_num = args.port_num
        pg_num = args.pg
        min_thr = args.min_thr
        shared_thr = args.shared_thr
        headroom_thr = args.headroom_thr
        xoff_enable = args.xoff_enable
        shared_xon_thr = args.shared_xon_thr
        self._qos_cmd_obj.ingress_priority_group(port_num=port_num, pg_num=pg_num, min_thr=min_thr,
                                                 shared_thr=shared_thr, shared_xon_thr=shared_xon_thr,
                                                 headroom_thr=headroom_thr, xoff_enable=xoff_enable, update=True)

    def set_hnu_qos_ingress_pg(self, args):
        port_num = args.port_num
        pg_num = args.pg
        min_thr = args.min_thr
        shared_thr = args.shared_thr
        headroom_thr = args.headroom_thr
        xoff_enable = args.xoff_enable
        shared_xon_thr = args.shared_xon_thr
        self._qos_cmd_obj.ingress_priority_group(port_num=port_num, pg_num=pg_num, min_thr=min_thr,
                                                 shared_thr=shared_thr, shared_xon_thr=shared_xon_thr,
                                                 headroom_thr=headroom_thr, xoff_enable=xoff_enable, update=True, mode='hnu')

    def get_qos_ingress_pg(self, args):
        port_num = args.port_num
        pg_num = args.pg
        self._qos_cmd_obj.ingress_priority_group(port_num=port_num, pg_num=pg_num, update=False)

    def get_hnu_qos_ingress_pg(self, args):
        port_num = args.port_num
        pg_num = args.pg
        self._qos_cmd_obj.ingress_priority_group(port_num=port_num, pg_num=pg_num, update=False, mode='hnu')

    def set_qos_ingress_pg_map(self, args):
        port_num = args.port_num
        map_list = args.map_list
        self._qos_cmd_obj.ingress_priority_to_pg_map(port_num=port_num, map_list=map_list, update=True)

    def set_hnu_qos_ingress_pg_map(self, args):
        port_num = args.port_num
        map_list = args.map_list
        self._qos_cmd_obj.ingress_priority_to_pg_map(port_num=port_num, map_list=map_list, update=True, mode='hnu')

    def get_qos_ingress_pg_map(self, args):
        port_num = args.port_num
        self._qos_cmd_obj.ingress_priority_to_pg_map(port_num=port_num, update=False)

    def get_hnu_qos_ingress_pg_map(self, args):
        port_num = args.port_num
        self._qos_cmd_obj.ingress_priority_to_pg_map(port_num=port_num, update=False, mode='hnu')

    def set_qos_pfc_enable(self, args):
        self._qos_cmd_obj.pfc(enable=True, update=True)

    def set_hnu_qos_pfc_enable(self, args):
        self._qos_cmd_obj.pfc(enable=True, update=True, mode='hnu')

    def set_qos_pfc_disable(self, args):
        self._qos_cmd_obj.pfc(update=True, disable=True)

    def set_hnu_qos_pfc_disable(self, args):
        self._qos_cmd_obj.pfc(update=True, disable=True, mode='hnu')

    def get_qos_pfc(self, args):
        self._qos_cmd_obj.pfc(update=False)

    def get_hnu_qos_pfc(self, args):
        self._qos_cmd_obj.pfc(update=False, mode='hnu')

    def set_qos_arb_cfg(self, args):
        enable = args.en
        self._qos_cmd_obj.arb_cfg(en=enable, update=True)

    def set_hnu_qos_arb_cfg(self, args):
        enable = args.en
        self._qos_cmd_obj.arb_cfg(en=enable, update=True, mode='hnu')

    def get_qos_arb_cfg(self, args):
        self._qos_cmd_obj.arb_cfg(update=False)

    def get_hnu_qos_arb_cfg(self, args):
        self._qos_cmd_obj.arb_cfg(update=False, mode='hnu')

    def set_qos_xoff_status(self, args):
        port_num = args.port_num
        pg = args.pg
        status = args.status
        self._qos_cmd_obj.xoff_status(port_num=port_num, pg=pg, status=status, update=True)

    def set_hnu_qos_xoff_status(self, args):
        port_num = args.port_num
        pg = args.pg
        status = args.status
        self._qos_cmd_obj.xoff_status(port_num=port_num, pg=pg, status=status, update=True, mode='hnu')

    def get_qos_xoff_status(self, args):
        port_num = args.port_num
        pg = args.pg
        self._qos_cmd_obj.xoff_status(port_num=port_num, pg=pg, update=False)

    def get_hnu_qos_xoff_status(self, args):
        port_num = args.port_num
        pg = args.pg
        self._qos_cmd_obj.xoff_status(port_num=port_num, pg=pg, update=False, mode='hnu')

    def peek_fpg_stats(self, args):
        port_num = args.port_num
        iterations = args.iters
        grep_regex = args.grep
        self._peek_cmd_obj.peek_fpg_stats(port_num=port_num, iterations=iterations, grep_regex=grep_regex)

    def peek_hnu_fpg_stats(self, args):
        port_num = args.port_num
        grep_regex = args.grep
        self._peek_cmd_obj.peek_fpg_stats(port_num=port_num, grep_regex=grep_regex, mode='hnu')

    def peek_psw_nu_stats(self, args):
        port_num = args.port_num
        queues = args.queues
        iterations = args.iters
        grep_regex = args.grep
        self._peek_cmd_obj.peek_psw_stats(mode='nu', port_num=port_num, queue_list=queues, grep_regex=grep_regex, iterations=iterations, psw_ext=False)

    def peek_psw_hnu_stats(self, args):
        port_num = args.port_num
        queues = args.queues
        grep_regex = args.grep
        self._peek_cmd_obj.peek_psw_stats(mode='hnu', port_num=port_num, queue_list=queues, grep_regex=grep_regex, psw_ext=False)

    def peek_psw_ext_nu_stats(self, args):
        port_num = args.port_num
        queues = args.queues
        iterations = args.iters
        grep_regex = args.grep
        self._peek_cmd_obj.peek_psw_stats(mode='nu', port_num=port_num, queue_list=queues, grep_regex=grep_regex, iterations=iterations, psw_ext=True)

    def peek_meter_stats(self, args):
        bank = args.bank
        index = args.index
        grep_regex = args.grep
        self._peek_cmd_obj.peek_meter_stats(bank=bank, index=index, grep_regex=grep_regex)

    def peek_fun_malloc_slot_stats(self, args):
        non_coh = args.non_coh
        self._funos_cmd_obj.peek_fun_malloc_slot_stats(non_coh)

    def peek_malloc_caches_slot_stats(self, args):
        slot = args.slot
        non_coh = args.non_coh
        grep_regex = args.grep
        self._funos_cmd_obj.peek_malloc_caches_slot_stats(slot, non_coh, grep_regex=grep_regex)

    def peek_erp_meter_stats(self, args):
        bank = args.bank
        index = args.index
        grep_regex = args.grep
        self._peek_cmd_obj.peek_meter_stats(bank=bank, index=index, grep_regex=grep_regex, erp=True)

    def peek_vp_stats(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_vp_stats(grep_regex=grep_regex, iterations=iterations)

    def peek_fcp_tunnel_stats(self, args):
        tunnel_id = args.tunnel
        grep_regex = args.grep
        self._peek_cmd_obj.peek_fcp_tunnel_stats(tunnel_id=tunnel_id, grep_regex=grep_regex)

    def peek_fcp_paths_stats(self, args):
        path_id = args.path_id
        self._peek_cmd_obj.peek_fcp_path_stats(path_id=path_id)

    def peek_fcp_tunnels_stats(self, args):
        tunnel_id = args.tunnel
        path_id = args.path_id
        self._peek_cmd_obj.peek_fcp_stats_tunnel_stats(tunnel_id=tunnel_id,path_id = args.path_id)

    def peek_wro_nu_stats(self, args):
        tunnel_id = args.tunnel
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_wro_stats(mode='nu', tunnel_id=tunnel_id, grep_regex=grep_regex, iterations=iterations)

    def peek_wro_hnu_stats(self, args):
        tunnel_id = args.tunnel
        grep_regex = args.grep
        self._peek_cmd_obj.peek_wro_stats(mode='hnu', tunnel_id=tunnel_id, grep_regex=grep_regex)

    def peek_fwd_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_fwd_stats(grep_regex=grep_regex)

    def peek_erp_hnu_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_erp_stats(mode='hnu', grep_regex=grep_regex)

    def peek_erp_nu_stats(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_erp_stats(mode='nu', grep_regex=grep_regex, iterations=iterations)

    def peek_etp_hnu_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_etp_stats(mode='hnu', grep_regex=grep_regex)

    def peek_etp_nu_stats(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_etp_stats(mode='nu', grep_regex=grep_regex, iterations=iterations)

    def peek_erp_flex_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_erp_stats(mode='flex', grep_regex=grep_regex)

    def peek_nu_parser_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_parser_stats(mode='nu', grep_regex=grep_regex)

    def peek_hnu_parser_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_parser_stats(mode='hnu', grep_regex=grep_regex)

    def peek_nu_qos_wred_ecn_stats(self, args):
        port_num = args.port_num
        queue_num = args.queue_num
        grep_regex = args.grep
        self._peek_cmd_obj.peek_wred_ecn_stats(port_num=port_num, queue_num=queue_num, grep_regex=grep_regex)

    def peek_nu_sfg_stats(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_sfg_stats(mode='nu', grep_regex=grep_regex, iterations=iterations, sfg_ext=False)

    def peek_hnu_sfg_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_sfg_stats(mode='hnu', grep_regex=grep_regex)

    def peek_nu_sfg_ext_stats(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_sfg_stats(mode='nu', grep_regex=grep_regex, iterations=iterations, sfg_ext=True)

    def peek_nu_flowcontrol_stats(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_nu_flowcontrol(grep_regex=grep_regex, iterations=iterations)

    def peek_per_vp_stats(self, args):
        grep_regex = args.grep
        pp = args.pp
        rx = args.rx
        tx = args.tx
        q = args.q
        iterations = args.iters
        cluster_id = args.cluster_id
        core_id = args.core_id
        cid_flag = True
        core_id_flag = True
        if cluster_id is not None:
            cid_flag = self.check_cluster_id_range(cluster_id=cluster_id)
        if core_id is not None:
            core_id_flag = self.check_core_id_range(core_id=core_id)
        if core_id and (cluster_id is None):
            print "Please enter value for cluster_id with core_id"
            return self.dpc_client.disconnect()
        if cid_flag and core_id_flag and pp:
            self._peek_cmd_obj.peek_stats_per_vp_pp(cluster_id=cluster_id, core_id=core_id, rx=rx, tx=tx, q=q,
                                                    grep_regex=grep_regex, iterations=iterations)
        elif cid_flag and core_id_flag:
            self._peek_cmd_obj.peek_stats_per_vp(cluster_id=cluster_id, core_id=core_id, rx=rx, tx=tx, q=q,
                                                 grep_regex=grep_regex, iterations=iterations)

    def peek_l1_cache_stats(self, args):
        grep_regex = args.grep
        pp = args.pp
        load = args.load_miss
        store = args.store_miss
        cluster_id = args.cluster_id
        core_id = args.core_id
        iterations = args.iters
        cid_flag = True
        core_id_flag = True
        if cluster_id is not None:
            cid_flag = self.check_cluster_id_range(cluster_id=cluster_id)
        if core_id is not None:
            core_id_flag = self.check_core_id_range(core_id=core_id)
        if core_id and (cluster_id is None):
            print "Please enter value for cluster_id with core_id"
            return self.dpc_client.disconnect()
        self._peek_cmd_obj.peek_stats_l1_cache_pp(cluster_id=cluster_id, core_id=core_id, load=load, store=store,
                                                grep_regex=grep_regex, iterations=iterations)

    def peek_nwqm_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_nwqm_stats(grep_regex=grep_regex)

    def peek_nwqm_hnu_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_nwqm_stats(mode='hnu', grep_regex=grep_regex)

    def peek_fae_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_fae_stats(grep_regex=grep_regex)

    def peek_hbm_stats(self, args):
        grep_regex = args.grep
        muh = args.muh
        self._peek_cmd_obj.peek_hbm_stats(muh=muh, grep_regex=grep_regex)

    def peek_mpg_stats(self, args):
        self._peek_cmd_obj.peek_mpg_stats()

    def peek_pervppkts_stats(self, args):
        grep_regex = args.grep
        cluster_id = args.cluster_id
        core_id = args.core_id
        iterations = args.iters
        cid_flag = True
        core_id_flag = True
        if cluster_id is not None:
            cid_flag = self.check_cluster_id_range(cluster_id=cluster_id)
        if core_id is not None:
            core_id_flag = self.check_core_id_range(core_id=core_id)
        if core_id and not cluster_id:
            print "Please enter value for cluster_id with "
            return self.dpc_client.disconnect()
        if cid_flag and core_id_flag:
            self._peek_cmd_obj.peek_pervppkts_stats(cluster_id=cluster_id, core_id=core_id, grep_regex=grep_regex, iterations=iterations)

    def peek_stats_nhp(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_nhp_stats(grep_regex=grep_regex, iterations=iterations, nhp_ext=False)

    def peek_stats_nhp_ext(self, args):
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_nhp_stats(grep_regex=grep_regex, iterations=iterations, nhp_ext=True)

    def peek_stats_sse(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_sse_stats(grep_regex=grep_regex, sse_ext=False)

    def peek_stats_sse_ext(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_sse_stats(grep_regex=grep_regex, sse_ext=True)

    def peek_pc_resource_stats(self, args):
        grep_regex = args.grep
        cluster_id = args.cluster_id
        core_id = args.core_id
        iterations = args.iters
        cid_flag = True
        core_id_flag = True
        if cluster_id is not None:
            cid_flag = self.check_cluster_id_range(cluster_id=cluster_id)
        if core_id is not None:
            core_id_flag = self.check_core_id_range(core_id=core_id)
        if core_id and not cluster_id:
            print "Please enter value for cluster_id with "
            return self.dpc_client.disconnect()
        if cid_flag and core_id_flag:
            self._peek_cmd_obj.peek_pc_resource_stats(cluster_id=cluster_id, core_id=core_id, grep_regex=grep_regex, iterations=iterations)

    def peek_cc_resource_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_cc_resource_stats(grep_regex=grep_regex)

    def peek_dma_resource_stats(self, args):
        cluster_id = args.cluster_id
        self._peek_cmd_obj.peek_dma_resource_stats(cluster_id=cluster_id)

    def peek_le_resource_stats(self, args):
        cluster_id = args.cluster_id
        self._peek_cmd_obj.peek_le_resource_stats(cluster_id=cluster_id)

    def peek_zip_resource_stats(self, args):
        cluster_id = args.cluster_id
        self._peek_cmd_obj.peek_zip_resource_stats(cluster_id=cluster_id)

    def peek_rgx_resource_stats(self, args):
        grep_regex = args.grep
        cluster_id = args.cluster_id
        self._peek_cmd_obj.peek_rgx_resource_stats(cluster_id=cluster_id, grep_regex=grep_regex)

    def peek_hnu_resource_stats(self, args):
        grep_regex = args.grep
        resource_id = args.resource_id
        self._peek_cmd_obj.peek_mode_resource_stats(mode='hnu', resource_id=resource_id, grep_regex=grep_regex)

    def peek_nu_resource_stats(self, args):
        grep_regex = args.grep
        resource_id = args.resource_id
        iterations = args.iters
        self._peek_cmd_obj.peek_mode_resource_stats(mode='nu', resource_id=resource_id, grep_regex=grep_regex, iterations=iterations)

    def peek_hu_resource_stats(self, args):
        id = args.id
        grep_regex = args.grep
        self._peek_cmd_obj.peek_hu_resource_stats(hu_id=id, grep_regex=grep_regex)

    def peek_hu_wqsi_resource_stats(self, args):
        id = args.id
        grep_regex = args.grep
        resource_id = args.rid
        self._peek_cmd_obj.peek_hu_resource_stats(hu_id=id, wqsi=True, resource_id=resource_id,
                                                  grep_regex=grep_regex)

    def peek_hu_wqse_resource_stats(self, args):
        id = args.id
        grep_regex = args.grep
        self._peek_cmd_obj.peek_hu_resource_stats(hu_id=id, wqse=True, grep_regex=grep_regex)

    def peek_hux_resource_stats(self, args):
        id = args.id
        iterations = args.iters
        grep_regex = args.grep
        self._peek_cmd_obj.peek_hux_resource_stats(hu_id=id, grep_regex=grep_regex, iterations=iterations)

    def peek_dam_resource_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_dam_resource_stats(grep_regex=grep_regex)

    def get_nu_configs(self, args):
        config_type = args.config_type
        if not config_type in ['pool_config', 'ncv_config', 'per_pool_flow_control', 'global_flow_control']:
            print "Please give config_type in: \n1. pool_config\n2. ncv_config\n3. per_pool_flow_control\n4. global_flow_control"
            self.dpc_client.disconnect()
        self._peek_cmd_obj.get_nu_configs(config_type=config_type)

    def get_bam_configs(self, args):
        self._peek_cmd_obj.get_bam_usage()

    def peek_bam_resource_stats(self, args):
        grep_regex = args.grep
        cid = args.cid
        diff = args.diff
        iterations = args.iters
        self._peek_cmd_obj.peek_bam_resource_stats(cid=cid, diff=diff, grep_regex=grep_regex, iterations=iterations)

    def peek_ocm_resource_stats(self, args):
        grep_regex = args.grep
        iterations = args.iters
        diff = args.diff
        self._peek_cmd_obj.peek_ocm_resource_stats(diff=diff, grep_regex=grep_regex, iterations=iterations)

    def peek_eqm_stats(self, args):
        drg_ctx = args.drg_ctx
        evq = args.evq
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_eqm_stats(drg_ctx=drg_ctx, evq=evq, grep_regex=grep_regex, iterations=iterations)

    def peek_malloc_agent_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_malloc_agent_stats(grep_regex=grep_regex)

    def peek_malloc_agent_non_coh_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_malloc_agent_non_coh_stats(grep_regex=grep_regex)

    def peek_funtop_stats(self, args):
        self._peek_cmd_obj.peek_funtop_stats()

    def peek_wustacks_stats(self, args):
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_wustacks(iterations=iterations)

    def peek_wus_stats(self, args):
        self._peek_cmd_obj.peek_stats_wus()

    def peek_cdu_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_cdu_stats(grep=grep, iterations=iterations)

    def peek_ca_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_ca_stats(grep=grep, iterations=iterations)

    def peek_ddr_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_ddr_stats(grep=grep, iterations=iterations)

    def peek_mud_stats(self, args):
        grep = args.grep
        iterations = args.iters
        qdepth = args.qd
        self._peek_cmd_obj.peek_stats_mud(qdepth=qdepth, iterations=iterations, grep_regex=grep)

    def peek_dam_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_dam(iterations=iterations, grep_regex=grep)

    def peek_malloc_caches_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_malloc_caches(iterations=iterations, grep_regex=grep)

    def peek_mbuf_stats(self, args):
        iterations = args.iters
        vp = args.vp
        mem_type = args.mem_type
        if mem_type:
            self._peek_cmd_obj.peek_stats_mbuf_mem_type(iterations=iterations)
        else:
            self._peek_cmd_obj.peek_stats_mbuf_vp(iterations=iterations)

    def peek_l2_cache_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_l2_cache_stats(grep=grep, iterations=iterations)

    def peek_le_tables_sdn_in(self, args):
        grep = args.grep
        self._peek_cmd_obj.peek_le_tables_sdn_in(grep=grep)

    def peek_le_tables_sdn_out(self, args):
        grep = args.grep
        self._peek_cmd_obj.peek_le_tables_sdn_out(grep=grep)

    def peek_sdn_stats(self, args):
        offset = args.offset
        num_flows = args.num_flows
        print offset, num_flows
        self._peek_cmd_obj.peek_sdn_stats(offset=offset, num_flows=num_flows)

    def peek_vr_flow_stats(self, args):
        offset = args.offset
        num_flows = args.num_flows
        print offset, num_flows
        self._peek_cmd_obj.peek_vr_flow_stats(offset=offset, num_flows=num_flows)

    def peek_sdn_meter_stats(self, args):
        policy_id = args.policy_id
        direction = args.direction
        self._peek_cmd_obj.peek_sdn_meter_stats(policy_id, direction)

    def peek_sdn_flow_stats(self, args):
        self._peek_cmd_obj.peek_sdn_flow_stats()

    def peek_sdn_vp_stats(self,args):
        grep = args.grep
        self._peek_cmd_obj.peek_sdn_vp_stats(grep=grep)

    def peek_tcp_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_tcp_stats(grep=grep, iterations=iterations)

    def peek_tcp_flows_summary_stats(self,args):
        flow_id = args.flow_id
        count = args.count
        self._peek_cmd_obj.peek_tcp_flows_summary_stats(flow_id = flow_id,count = count)

    def peek_tcp_flows_details(self,args):
        count = args.count
        dest = args.dest
        iterations = args.iters
        self._peek_cmd_obj.peek_tcp_flows_details(count = count, dest = dest, iterations = iterations)

    def peek_tcp_flows_state_all(self,args):
        count = args.count 
        self._peek_cmd_obj.peek_tcp_flows_state(count=count)

    def peek_tcp_flows_state_filter(self,args):
        sip = args.sip 
        dip = args.dip 
        sport = args.sport 
        dport = args.dport 
        count = args.count
        flow_id = args.flow_id 
        self._peek_cmd_obj.peek_tcp_flows_state(flow_id=flow_id,sip=sip,dip=dip,sport=sport,dport=dport,count=count)

    def peek_tcp_flows_fc_all(self,args):
        count = args.count
        self._peek_cmd_obj.peek_tcp_flows_fc(count=count)

    def peek_tcp_flows_fc_filter(self,args):
        sip = args.sip
        dip = args.dip
        sport = args.sport
        dport = args.dport
        count = args.count
        flow_id = args.flow_id
        self._peek_cmd_obj.peek_tcp_flows_fc(flow_id=flow_id,sip=sip,dip=dip,sport=sport,dport=dport,count=count)
   
    def peek_stats_rate_all(self,args):
        rate = True
        count = args.count
        iterations = args.iters
        self._peek_cmd_obj.peek_tcp_flows_stats(count=count,rate=rate, iterations=iterations)

    def peek_stats_rate_filter(self,args):
        sip = args.sip
        dip = args.dip
        sport = args.sport
        dport = args.dport
        count = args.count
        flow_id = args.flow_id
        rate = True
        self._peek_cmd_obj.peek_tcp_flows_stats(flow_id=flow_id,sip=sip,dip=dip,sport=sport,dport=dport,count=count,rate=rate)
    
    def peek_stats_drops_all(self,args):
        drops = True
        count = args.count
        self._peek_cmd_obj.peek_tcp_flows_stats(count=count,drops=drops)

    def peek_stats_drops_filter(self,args):
        sip = args.sip
        dip = args.dip
        sport = args.sport
        dport = args.dport
        count = args.count
        flow_id = args.flow_id
        drops = True
        self._peek_cmd_obj.peek_tcp_flows_stats(flow_id=flow_id,sip=sip,dip=dip,sport=sport,dport=dport,count=count,drops=drops)

    def peek_stats_other_all(self,args):
        other = True
        count = args.count
        self._peek_cmd_obj.peek_tcp_flows_stats(count=count,other=other)

    def peek_stats_other_filter(self,args):
        sip = args.sip
        dip = args.dip
        sport = args.sport
        dport = args.dport
        count = args.count
        flow_id = args.flow_id
        other = True
        self._peek_cmd_obj.peek_tcp_flows_stats(flow_id=flow_id,sip=sip,dip=dip,sport=sport,dport=dport,count=count,other=other)

    def peek_probetest_summary(self,args):
        summary = True
        self._peek_cmd_obj.peek_stats_probetest(summary=summary)

    def peek_probetest_localityinfo(self,args):
        localityinfo = True
        self._peek_cmd_obj.peek_stats_probetest(localityinfo=localityinfo)

    def peek_probetest_pathinfo(self,args):
        path_id = args.path_id
        status = args.status
        pathinfo = True
        self._peek_cmd_obj.peek_stats_probetest(pathinfo=pathinfo,path_id=path_id,status=status)

    def peek_probetest_tunnelinfo(self,args):
        tunnelinfo = True
        self._peek_cmd_obj.peek_stats_probetest(tunnelinfo=tunnelinfo)

    def peek_probetest_streaminfo(self,args):
        streaminfo = True
        self._peek_cmd_obj.peek_stats_probetest(streaminfo=streaminfo)

    def set_probetest_basic(self,args):
        locality=args.locality
        self._peek_cmd_obj.set_nu_probetest(locality=locality)

    def set_probetest_setpath(self,args):
        setpath = True
        path_index = args.path_index
        state = args.state
        status = args.status
        self._peek_cmd_obj.set_nu_probetest(setpath=setpath,path_index=path_index,state=state,status=status)

    def set_probetest_reset(self,args):
        reset = True
        self._peek_cmd_obj.set_nu_probetest(reset=reset)

    def set_probetest_localtrigger(self,args):
        localtrigger = True
        self._peek_cmd_obj.set_nu_probetest(localtrigger=localtrigger)

    def set_probetest_nacktrigger(self,args):
        nacktrigger = True
        path_index = args.path_index
        self._peek_cmd_obj.set_nu_probetest(nacktrigger=nacktrigger,path_index=path_index)

    def set_probetest_rcvprobe(self,args):
        rcvprobe = True
        path_index = args.path_index
        self._peek_cmd_obj.set_nu_probetest(rcvprobe=rcvprobe,path_index=path_index)

    def set_probetest_setuppath(self,args):
        setuppath = True
        path_index = args.path_index
        inner_dip = args.inner_dip
        self._peek_cmd_obj.set_nu_probetest(setuppath=setuppath,path_index=path_index,inner_dip=inner_dip)

    def peek_copp_stats(self, args):
        grep = args.grep
        self._peek_cmd_obj.peek_copp_stats(grep=grep)

    def peek_rdsock_stats(self, args):
        grep = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_rdsock_flow_stats(grep_regex=grep, iterations=iterations)
    
    def peek_hu_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_stats_hu(grep_regex=grep_regex)

    def peek_hu_pcie_stats(self, args):
        hu_id = args.hu_id
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_hu_pcie(hu_id=hu_id, grep_regex=grep_regex, iterations=iterations)

    def peek_hu_fc_stats(self, args):
        hu_id = args.hu_id
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_hu_fc(hu_id=hu_id, grep_regex=grep_regex, iterations=iterations)

    def peek_hu_link_stats(self, args):
        hu_id = args.hu_id
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_hu_link(hu_id=hu_id, grep_regex=grep_regex, iterations=iterations)

    def peek_hu_pwp_stats(self, args):
        hu_id = args.hu_id
        grep_regex = args.grep
        iterations = args.iters
        self._peek_cmd_obj.peek_stats_hu_pwp(hu_id=hu_id, grep_regex=grep_regex, iterations=iterations)

    def peek_hu_framer_stats(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_stats_hu_framer(grep_regex=grep_regex)

    # Storage Peek stats
    def peek_stats_ssds(self, args):
        grep = args.grep
        ssd_ids = args.ssd_ids
        self._storage_peek_obj.peek_connected_ssds(ssd_ids=ssd_ids, grep=grep)

    def peek_blt_vol_stats(self, args):
        vol_id = args.vol_id
        self._storage_peek_obj.peek_blt_vol_stats(vol_id=vol_id)

    def peek_rds_vol_stats(self, args):
        vol_id = args.vol_id
        self._storage_peek_obj.peek_rds_vol_stats(vol_id=vol_id)

    def peek_nhp_status(self, args):
        grep_regex = args.grep
        self._peek_cmd_obj.peek_nhp_status(grep_regex=grep_regex)

    def clear_nu_port_stats(self, args):
        self._clear_cmd_obj.clear_nu_port_stats(port_num=args.port_num, shape=args.shape)

    def clear_nu_fwd_stats(self, args):
        self._clear_cmd_obj.clear_nu_fwd_stats()

    def clear_nu_erp_stats(self, args):
        self._clear_cmd_obj.clear_nu_erp_stats()

    def clear_nu_parser_stats(self, args):
        self._clear_cmd_obj.clear_nu_parser_stats()

    def clear_nu_nwqm_stats(self, args):
        self._clear_cmd_obj.clear_nu_nwqm_stats()

    def clear_nu_vppkts_stats(self, args):
        self._clear_cmd_obj.clear_nu_vppkts_stats()

    def clear_nu_all_stats(self, args):
        self._clear_cmd_obj.clear_nu_all_stats()

    def set_port_speed(self, args):
        port_num = args.port_num
        shape = args.shape
        brkmode = args.brkmode
        self._port_cmd_obj.port_speed(port_num=port_num, shape=shape, brkmode=brkmode)

    def get_port_speed(self, args):
        port_num = args.port_num
        shape = args.shape
        self._port_cmd_obj.port_speed(port_num=port_num, shape=shape)

    def set_sample(self, args, mode):
        id = args.id
        fpg = args.fpg
        dest = args.dest
        acl = args.acl
        flag_mask = args.flag_mask
        hu = args.hu
        psw_drop = args.psw_drop
        pps_en = args.pps_en
        pps_interval = args.pps_interval
        pps_burst = args.pps_burst
        pps_tick = args.pps_tick
        sampler_en = args.sampler_en
        sampler_rate = args.sampler_rate
        sampler_run_sz = args.sampler_run_sz
        first_cell_only = args.first_cell_only
        self._sample_cmd_obj.set_sample(id=id, fpg=fpg, dest=dest, acl=acl, flag_mask=flag_mask, hu=hu, psw_drop=psw_drop,
                                        pps_en=pps_en, pps_interval=pps_interval, pps_burst=pps_burst, pps_tick=pps_tick,
                                        sampler_en=sampler_en, sampler_rate=sampler_rate, sampler_run_sz=sampler_run_sz,
                                        first_cell_only=first_cell_only, mode=mode)

    def set_ingress_sample(self, args):
        self.set_sample(args=args, mode=0)

    def set_egress_sample(self, args):
        self.set_sample(args=args, mode=1)

    def disable_sample(self, args):
        self.set_sample(args=args, mode=2)

    def get_sample(self, args):
        self._sample_cmd_obj.get_sample()

    def show_tech_nu_stats(self, args):
        filename = args.filename
        portlist = args.portlist
        fcp_tunnel_id = args.fcp_tunnel_id
        self._show_cmd_obj.show_stats(filename=filename, mode='nu', port_list=portlist, fcp_tunnel_id=fcp_tunnel_id)

    def show_tech_hnu_stats(self, args):
        filename = args.filename
        portlist = args.portlist
        fcp_tunnel_id = args.fcp_tunnel_id
        self._show_cmd_obj.show_stats(filename=filename, mode='hnu', port_list=portlist, fcp_tunnel_id=fcp_tunnel_id)

    def show_tech_all_stats(self, args):
        filename = args.filename
        portlist = args.portlist
        fcp_tunnel_id = args.fcp_tunnel_id
        self._show_cmd_obj.show_stats(filename=filename, mode='all', port_list=portlist, fcp_tunnel_id=fcp_tunnel_id)

    def show_k2_stats(self, args):
        filename = args.filename
        iterations = args.iters 
        self._show_cmd_obj.show_k2_stats(filename=filename, iterations=iterations) 

    def get_flow_list(self, args):
        grep_regex = args.grep
        pp = args.pp
        hu_id = args.hu_id
        hcf_id = args.hcf_id
        storage = args.storage
        iterations = args.iters
        tx = args.tx
        rx = args.rx
        if tx is None and rx is None:
            tx=1
            rx=1
        if pp:
            if hcf_id and (('.' not in hcf_id) or len(hcf_id.split(".")) != 3):
                print "Please enter hcf_id(hu.cntrl.fnid) in x.x.x format. Current given %s" % hcf_id
                return self.dpc_client.disconnect()
            elif hu_id and hcf_id:
                print "Please enter either hu_id in x or hcf_id in x.x.x format"
                return self.dpc_client.disconnect()
            self._flow_cmd_obj.get_flow_list_pp(hcf_id=hcf_id, hu_id=hu_id, tx=tx, rx=rx, storage=storage, grep_regex=grep_regex, iterations=iterations)
        else:
            self._flow_cmd_obj.get_flow_list(hcf_id=hcf_id, hu_id=hu_id, grep_regex=grep_regex)

    def flow_list_rdma(self, args):
        grep_regex = args.grep
        hu_id = args.hu_id
        qpn_number = args.qpn
        self._flow_cmd_obj.get_flow_list_rdma(hu_id=hu_id, qpn_number=qpn_number, grep_regex=grep_regex)

    def peek_stats_rdma(self, args):
        grep_regex = args.grep
        hu_id = args.hu_id
        qpn_number = args.qpn
        self._peek_cmd_obj.peek_stats_rdma(hu_id=hu_id, qpn_number=qpn_number, grep_regex=grep_regex)

    def get_flow_blocked(self, args):
        grep_regex = args.grep
        self._flow_cmd_obj.get_flow_blocked(grep_regex=grep_regex)

    def debug_vp_state(self, args):
        vp_num = args.vp_num
        grep_regex = args.grep
        self._debug_cmd_obj.debug_vp_state(vp_num, grep_regex)

    def debug_vp_util(self, args):
        grep_regex = args.grep
        pp = args.pp
        cluster_id = args.cluster_id
        core_id = args.core_id
        cid_flag = True
        core_id_flag = True
        if cluster_id is not None:
            cid_flag = self.check_cluster_id_range(cluster_id=cluster_id)
        if core_id is not None:
            core_id_flag = self.check_core_id_range(core_id=core_id)
        if core_id and (cluster_id is None):
            print "Please enter value for cluster_id with core_id"
            return self.dpc_client.disconnect()
        if cid_flag and core_id_flag and pp:
            self._debug_cmd_obj.debug_vp_util_pp(cluster_id=cluster_id, core_id=core_id, grep_regex=grep_regex)
        elif cid_flag and core_id_flag:
            self._debug_cmd_obj.debug_vp_util(cluster_id=cluster_id, core_id=core_id, grep_regex=grep_regex)

    # Peek storage commands
    def peek_storage_vols(self, args):
        grep = args.grep
        self._storage_peek_obj.peek_storage_volumes(grep=grep)

    def peek_fcp_nu_gph(self,args):
        gph_cache = True
        self._peek_cmd_obj.peek_stats_fcp_nu_gph(gph_cache=gph_cache)

    def peek_stats_nhp_status(self,args):
        self._peek_cmd_obj.peek_stats_nhp_status()

    # storage commands
    def storage_list_vols(self, args):
        voltype = args.voltype
        if voltype == "blt":
            self._storage_obj.storage_list_volumes_blt(voltype = 'VOL_TYPE_BLK_LOCAL_THIN')
        elif voltype == "lsv":
            self._storage_obj.storage_list_volumes_lsv(voltype = 'VOL_TYPE_BLK_LSV')
        elif voltype == "rds":
            self._storage_obj.storage_list_volumes_rds(voltype = 'VOL_TYPE_BLK_RDS')
        elif voltype == "file":
            self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_BLK_FILE')
        elif voltype == "ec":
            self._storage_obj.storage_list_volumes_ec(voltype = 'VOL_TYPE_BLK_EC')
        elif voltype == "replica":
            self._storage_obj.storage_list_volumes_replica(voltype = 'VOL_TYPE_BLK_REPLICA')
        elif voltype == "nvmem":
           self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_BLK_NV_MEMORY')
        elif voltype == "pv":
           self._storage_obj.storage_list_volumes_pv(voltype = 'VOL_TYPE_BLK_PART_VOL')
        elif voltype == "memvol":
           self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_BLK_MEMORY')
        elif voltype == "sdk_memvol":
           self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_SDK_BLK_MEMORY')
        elif voltype == "all":
            self._storage_obj.storage_list_volumes_blt(voltype = 'VOL_TYPE_BLK_LOCAL_THIN')
            self._storage_obj.storage_list_volumes_rds(voltype = 'VOL_TYPE_BLK_RDS')
            self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_BLK_FILE')
            self._storage_obj.storage_list_volumes_ec(voltype = 'VOL_TYPE_BLK_EC')
            self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_BLK_NV_MEMORY')
	    self._storage_obj.storage_list_volumes_pv(voltype = 'VOL_TYPE_BLK_PART_VOL')
	    self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_BLK_LSV')
	    self._storage_obj.storage_list_volumes_replica(voltype = 'VOL_TYPE_BLK_REPLICA')
            self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_BLK_MEMORY')
            self._storage_obj.storage_list_volumes(voltype = 'VOL_TYPE_SDK_BLK_MEMORY')
        else:
            print "unknown voltype"

    def storage_list_ctrls(self, args):
        self._storage_obj.storage_list_controllers()

    def storage_list_dev(self, args):
       self._storage_obj.storage_list_devices()

    def storage_getsb(self,args):
        vol_uuid = args.vol_uuid
        self._storage_obj.storage_getsb_volume(vol_uuid)

    def storage_getinfo(self, args):
        vol_uuid = args.vol_uuid
        self._storage_obj.storage_getinfo_volume(vol_uuid)

    def storage_getmap(self, args):
        vol_uuid = args.vol_uuid
        slba = args.slba
        lbc = args.lbc
        self._storage_obj.storage_getmap_volume(vol_uuid, slba, lbc)

    def storage_vol_stats(self, args):
        vol_uuid = args.vol_uuid
        voltype = args.voltype
        if voltype == "blt":
            self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_BLK_LOCAL_THIN')
        elif voltype == "lsv":
            self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_BLK_LSV')
        elif voltype == "rds":
            self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_BLK_RDS')
        elif voltype == "file":
            self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_BLK_FILE')
        elif voltype == "ec":
            self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_BLK_EC')
        elif voltype == "replica":
            self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_BLK_REPLICA')
        elif voltype == "memvol":
	    self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_BLK_MEMORY')
	elif voltype == "sdk_memvol":
	    self._storage_obj.storage_volume_stats(vol_uuid, voltype = 'VOL_TYPE_SDK_BLK_MEMORY')
	else:
            print "Unknown voltype"

    def storage_ctrlr_stats(self, args):
        ctrlr_uuid = args.ctrlr_uuid
        rdsock_vp = args.rdsock_vp
        if rdsock_vp:
            self._storage_obj.storage_rdsock_vp_stats()
        else:
            self._storage_obj.storage_controller_stats(ctrlr_uuid)

    def storage_dev_stats(self, args):
        device_id = args.device_id
        self._storage_obj.storage_device_stats(device_id)

    def execute_cmd(self, args):
        verb = args.verb
        cmd = args.cmd
        self._execute_obj.execute_commands(verb, cmd)

    # Set handler functions for the sub commands

    # -------------- Port Command Handlers ----------------
    set_port_mtu_parser.set_defaults(func=set_port_mtu)
    get_port_mtu_parser.set_defaults(func=get_port_mtu)
    set_port_enable_parser.set_defaults(func=enable_port)
    set_port_disable_parser.set_defaults(func=disable_port)
    set_port_pause_enable_parser.set_defaults(func=enable_port_link_pause)
    set_port_pause_disable_parser.set_defaults(func=disable_port_link_pause)
    set_port_pause_tx_enable_parser.set_defaults(func=enable_port_tx_link_pause)
    set_port_pause_tx_disable_parser.set_defaults(func=disable_port_tx_link_pause)
    set_port_pause_quanta_parser.set_defaults(func=set_port_pause_quanta)
    get_port_pause_quanta_parser.set_defaults(func=get_port_pause_quanta)
    set_port_pause_threshold_parser.set_defaults(func=set_port_pause_threshold)
    get_port_pause_threshold_parser.set_defaults(func=get_port_pause_threshold)
    set_port_pfc_enable_parser.set_defaults(func=enable_port_pfc)
    set_port_pfc_disable_parser.set_defaults(func=disable_port_pfc)
    set_port_pfc_tx_enable_parser.set_defaults(func=enable_port_tx_pfc)
    set_port_pfc_tx_disable_parser.set_defaults(func=disable_port_tx_pfc)
    set_port_pfc_quanta_parser.set_defaults(func=set_port_pfc_quanta)
    get_port_pfc_quanta_parser.set_defaults(func=get_port_pfc_quanta)
    set_port_pfc_threshold_parser.set_defaults(func=set_port_pfc_threshold)
    get_port_pfc_threshold_parser.set_defaults(func=get_port_pfc_threshold)
    set_port_ptp_peer_delay_enable_parser.set_defaults(func=enable_port_ptp_peer_delay)
    set_port_ptp_peer_delay_disable_parser.set_defaults(func=disable_port_ptp_peer_delay)
    set_port_ptp_peer_delay_parser.set_defaults(func=set_port_ptp_peer_delay)
    get_port_ptp_peer_delay_parser.set_defaults(func=get_port_ptp_peer_delay)
    get_port_ptp_tx_ts_parser.set_defaults(func=get_port_ptp_tx_ts)
    set_port_ptp_1step_enable_parser.set_defaults(func=enable_port_ptp_1step)
    set_port_ptp_1step_disable_parser.set_defaults(func=disable_port_ptp_1step)
    set_port_runt_filter_parser.set_defaults(func=set_port_runt_filter)
    get_port_runt_filter_parser.set_defaults(func=dump_port_runt_filter)
    set_port_speed_parser.set_defaults(func=set_port_speed)
    get_port_speed_parser.set_defaults(func=get_port_speed)
    get_port_link_status_parser.set_defaults(func=get_port_link_status)

    # -------------- SDN flow --------------------------
    get_sdn_flow_parser.set_defaults(func=get_sdn_flow_layers)

    # -------------- System Command Handlers ----------------
    set_system_params_syslog_parser.set_defaults(func=set_system_syslog_level)
    set_system_time_interval_parser.set_defaults(func=set_system_time_interval)
    get_system_time_interval_parser.set_defaults(func=get_system_time_interval)
    get_system_params_syslog_parser.set_defaults(func=get_system_syslog_level)

    # --------------------Sample Commands Handlers -------------
    set_nu_sample_ingress_parser.set_defaults(func=set_ingress_sample)
    set_nu_sample_egress_parser.set_defaults(func=set_egress_sample)
    set_nu_sample_disable_parser.set_defaults(func=disable_sample)
    get_nu_sample_parser.set_defaults(func=get_sample)
    
    # --------------------Set nu probetest Handlers -------------
    set_nu_probetest_parser.set_defaults(func=set_probetest_basic)
    set_nu_probetest_setpath_parser.set_defaults(func=set_probetest_setpath)
    set_nu_probetest_reset_parser.set_defaults(func=set_probetest_reset)
    set_nu_probetest_localtrigger_parser.set_defaults(func=set_probetest_localtrigger)
    set_nu_probetest_nacktrigger_parser.set_defaults(func=set_probetest_nacktrigger)
    set_nu_probetest_rcvprobe_parser.set_defaults(func=set_probetest_rcvprobe)
    set_nu_probetest_setuppath_parser.set_defaults(func=set_probetest_setuppath)

    # --------------------Meter Commands Handlers -------------
    set_nu_meter_parser.set_defaults(func=set_nu_meter)
    
    # -------------- QoS Command Handlers ----------------
    set_qos_egress_buffer_pool_parser.set_defaults(func=set_qos_egress_buffer_pool)
    get_qos_egress_buffer_pool_parser.set_defaults(func=get_qos_egress_buffer_pool)
    set_qos_egress_port_buffer_parser.set_defaults(func=set_qos_egress_port_buffer)
    get_qos_egress_port_buffer_parser.set_defaults(func=get_qos_egress_port_buffer)
    set_qos_egress_queue_buffer_parser.set_defaults(func=set_qos_egress_queue_buffer)
    get_qos_egress_queue_buffer_parser.set_defaults(func=get_qos_egress_queue_buffer)
    set_qos_egress_priority_map_parser.set_defaults(func=set_qos_egress_priority_map)
    get_qos_egress_priority_map_parser.set_defaults(func=get_qos_egress_priority_map)
    get_qos_ecn_glb_sh_thresh_parser.set_defaults(func=get_qos_ecn_glb_sh_threshold)
    set_qos_ecn_glb_sh_thresh_parser.set_defaults(func=set_qos_ecn_glb_sh_threshold)
    set_qos_ecn_profile_parser.set_defaults(func=set_qos_ecn_profile)
    get_qos_ecn_profile_parser.set_defaults(func=get_qos_ecn_profile)
    set_qos_ecn_prob_parser.set_defaults(func=set_qos_ecn_prob)
    get_qos_ecn_prob_parser.set_defaults(func=get_qos_ecn_prob)
    set_qos_wred_profile_parser.set_defaults(func=set_qos_wred_profile)
    get_qos_wred_profile_parser.set_defaults(func=get_qos_wred_profile)
    set_qos_wred_prob_parser.set_defaults(func=set_qos_wred_prob)
    get_qos_wred_prob_parser.set_defaults(func=get_qos_wred_prob)
    set_qos_wred_avg_queue_config_parser.set_defaults(func=set_qos_wred_avg_q_config)
    get_qos_wred_avg_queue_config_parser.set_defaults(func=get_qos_wred_avg_q_config)
    set_qos_wred_queue_config_parser.set_defaults(func=set_qos_wred_queue_config)
    get_qos_wred_queue_config_parser.set_defaults(func=get_qos_wred_queue_config)
    get_qos_scheduler_config_parser.set_defaults(func=get_qos_scheduler_config)
    set_qos_scheduler_dwrr_parser.set_defaults(func=set_qos_scheduler_config_dwrr)
    set_qos_scheduler_shaper_parser.set_defaults(func=set_qos_scheduler_config_shaper)
    set_qos_scheduler_strict_priority_parser.set_defaults(func=set_qos_scheduler_config_strict_priority)
    set_qos_ingress_pg_parser.set_defaults(func=set_qos_ingress_pg)
    get_qos_ingress_pg_parser.set_defaults(func=get_qos_ingress_pg)
    set_qos_ingress_pg_map_parser.set_defaults(func=set_qos_ingress_pg_map)
    get_qos_ingress_pg_map_parser.set_defaults(func=get_qos_ingress_pg_map)
    set_qos_pfc_enable_parser.set_defaults(func=set_qos_pfc_enable)
    set_qos_pfc_disable_parser.set_defaults(func=set_qos_pfc_disable)
    get_qos_pfc_parser.set_defaults(func=get_qos_pfc)
    set_qos_arb_cfg_parser.set_defaults(func=set_qos_arb_cfg)
    get_qos_arb_cfg_parser.set_defaults(func=get_qos_arb_cfg)
    set_qos_xoff_status_parser.set_defaults(func=set_qos_xoff_status)
    get_qos_xoff_status_parser.set_defaults(func=get_qos_xoff_status)

    # -------------- QoS Command Handlers ----------------
    set_hnu_qos_egress_buffer_pool_parser.set_defaults(func=set_hnu_qos_egress_buffer_pool)
    get_hnu_qos_egress_buffer_pool_parser.set_defaults(func=get_hnu_qos_egress_buffer_pool)
    set_hnu_qos_egress_port_buffer_parser.set_defaults(func=set_hnu_qos_egress_port_buffer)
    get_hnu_qos_egress_port_buffer_parser.set_defaults(func=get_hnu_qos_egress_port_buffer)
    set_hnu_qos_egress_queue_buffer_parser.set_defaults(func=set_hnu_qos_egress_queue_buffer)
    get_hnu_qos_egress_queue_buffer_parser.set_defaults(func=get_hnu_qos_egress_queue_buffer)
    set_hnu_qos_egress_priority_map_parser.set_defaults(func=set_hnu_qos_egress_priority_map)
    get_hnu_qos_egress_priority_map_parser.set_defaults(func=get_hnu_qos_egress_priority_map)
    get_hnu_qos_ecn_glb_sh_thresh_parser.set_defaults(func=get_hnu_qos_ecn_glb_sh_threshold)
    set_hnu_qos_ecn_glb_sh_thresh_parser.set_defaults(func=set_hnu_qos_ecn_glb_sh_threshold)
    set_hnu_qos_ecn_profile_parser.set_defaults(func=set_hnu_qos_ecn_profile)
    get_hnu_qos_ecn_profile_parser.set_defaults(func=get_hnu_qos_ecn_profile)
    set_hnu_qos_ecn_prob_parser.set_defaults(func=set_hnu_qos_ecn_prob)
    get_hnu_qos_ecn_prob_parser.set_defaults(func=get_hnu_qos_ecn_prob)
    set_hnu_qos_wred_profile_parser.set_defaults(func=set_hnu_qos_wred_profile)
    get_hnu_qos_wred_profile_parser.set_defaults(func=get_hnu_qos_wred_profile)
    set_hnu_qos_wred_prob_parser.set_defaults(func=set_hnu_qos_wred_prob)
    get_hnu_qos_wred_prob_parser.set_defaults(func=get_hnu_qos_wred_prob)
    set_hnu_qos_wred_avg_queue_config_parser.set_defaults(func=set_hnu_qos_wred_avg_q_config)
    get_hnu_qos_wred_avg_queue_config_parser.set_defaults(func=get_hnu_qos_wred_avg_q_config)
    set_hnu_qos_wred_queue_config_parser.set_defaults(func=set_hnu_qos_wred_queue_config)
    get_hnu_qos_wred_queue_config_parser.set_defaults(func=get_hnu_qos_wred_queue_config)
    get_hnu_qos_scheduler_config_parser.set_defaults(func=get_hnu_qos_scheduler_config)
    set_hnu_qos_scheduler_dwrr_parser.set_defaults(func=set_hnu_qos_scheduler_config_dwrr)
    set_hnu_qos_scheduler_shaper_parser.set_defaults(func=set_hnu_qos_scheduler_config_shaper)
    set_hnu_qos_scheduler_strict_priority_parser.set_defaults(func=set_hnu_qos_scheduler_config_strict_priority)
    set_hnu_qos_ingress_pg_parser.set_defaults(func=set_hnu_qos_ingress_pg)
    get_hnu_qos_ingress_pg_parser.set_defaults(func=get_hnu_qos_ingress_pg)
    set_hnu_qos_ingress_pg_map_parser.set_defaults(func=set_hnu_qos_ingress_pg_map)
    get_hnu_qos_ingress_pg_map_parser.set_defaults(func=get_hnu_qos_ingress_pg_map)
    set_hnu_qos_pfc_enable_parser.set_defaults(func=set_hnu_qos_pfc_enable)
    set_hnu_qos_pfc_disable_parser.set_defaults(func=set_hnu_qos_pfc_disable)
    get_hnu_qos_pfc_parser.set_defaults(func=get_hnu_qos_pfc)
    set_hnu_qos_arb_cfg_parser.set_defaults(func=set_hnu_qos_arb_cfg)
    get_hnu_qos_arb_cfg_parser.set_defaults(func=get_hnu_qos_arb_cfg)
    set_hnu_qos_xoff_status_parser.set_defaults(func=set_hnu_qos_xoff_status)
    get_hnu_qos_xoff_status_parser.set_defaults(func=get_hnu_qos_xoff_status)
    get_nu_config_parser.set_defaults(func=get_nu_configs)
    get_bam_parser.set_defaults(func=get_bam_configs)

    # -------------- Peek Command Handlers ----------------
    peek_fpg_stats_parser.set_defaults(func=peek_fpg_stats)
    peek_hnu_fpg_stats_parser.set_defaults(func=peek_hnu_fpg_stats)
    peek_psw_nu_stats_parser.set_defaults(func=peek_psw_nu_stats)
    peek_psw_hnu_stats_parser.set_defaults(func=peek_psw_hnu_stats)
    peek_psw_ext_nu_stats_parser.set_defaults(func=peek_psw_ext_nu_stats)
    peek_meter_nu_stats_parser.set_defaults(func=peek_meter_stats)
    peek_meter_erp_stats_parser.set_defaults(func=peek_erp_meter_stats)
    peek_vp_stats_parser.set_defaults(func=peek_vp_stats)
    peek_fcp_nu_global_parser.set_defaults(func=peek_fcp_tunnel_stats)
    peek_fcp_nu_paths_parser.set_defaults(func=peek_fcp_paths_stats)
    peek_fcp_nu_tunnels_parser.set_defaults(func=peek_fcp_tunnels_stats)
    peek_wro_nu_stats_parser.set_defaults(func=peek_wro_nu_stats)
    peek_wro_hnu_stats_parser.set_defaults(func=peek_wro_hnu_stats)
    peek_fwd_stats_parser.set_defaults(func=peek_fwd_stats)
    peek_erp_hnu_stats_parser.set_defaults(func=peek_erp_hnu_stats)
    peek_erp_nu_stats_parser.set_defaults(func=peek_erp_nu_stats)
    peek_erp_flex_stats_parser.set_defaults(func=peek_erp_flex_stats)
    peek_parser_nu_stats_parser.set_defaults(func=peek_nu_parser_stats)
    peek_parser_hnu_stats_parser.set_defaults(func=peek_hnu_parser_stats)
    peek_wred_ecn_stats_parser.set_defaults(func=peek_nu_qos_wred_ecn_stats)
    peek_nu_sfg_stats_parser.set_defaults(func=peek_nu_sfg_stats)
    peek_nu_sfg_ext_stats_parser.set_defaults(func=peek_nu_sfg_ext_stats)
    peek_hnu_sfg_stats_parser.set_defaults(func=peek_hnu_sfg_stats)
    peek_flowcontrol_nu_parser.set_defaults(func=peek_nu_flowcontrol_stats)
    peek_per_vp_stats_parser.set_defaults(func=peek_per_vp_stats)
    peek_l1_cache_stats_parser.set_defaults(func=peek_l1_cache_stats)
    peek_nwqm_stats_parser.set_defaults(func=peek_nwqm_stats)
    peek_nwqm_hnu_stats_parser.set_defaults(func=peek_nwqm_hnu_stats)
    peek_fae_stats_parser.set_defaults(func=peek_fae_stats)
    peek_hbm_stats_parser.set_defaults(func=peek_hbm_stats)
    peek_mpg_stats_parser.set_defaults(func=peek_mpg_stats)
    peek_pervppkts_stats_parser.set_defaults(func=peek_pervppkts_stats)
    peek_nhp_stats_parser.set_defaults(func=peek_stats_nhp)
    peek_nhp_ext_stats_parser.set_defaults(func=peek_stats_nhp_ext)
    peek_sse_stats_parser.set_defaults(func=peek_stats_sse)
    peek_sse_ext_stats_parser.set_defaults(func=peek_stats_sse_ext)
    peek_pc_resource_stats_parser.set_defaults(func=peek_pc_resource_stats)
    peek_cc_resource_stats_parser.set_defaults(func=peek_cc_resource_stats)
    peek_dma_resource_stats_parser.set_defaults(func=peek_dma_resource_stats)
    peek_le_resource_stats_parser.set_defaults(func=peek_le_resource_stats)
    peek_zip_resource_stats_parser.set_defaults(func=peek_zip_resource_stats)
    peek_rgx_resource_stats_parser.set_defaults(func=peek_rgx_resource_stats)
    peek_hnu_resource_stats_parser.set_defaults(func=peek_hnu_resource_stats)
    peek_nu_resource_stats_parser.set_defaults(func=peek_nu_resource_stats)
    peek_hu_resource_stats_parser.set_defaults(func=peek_hu_resource_stats)
    peek_hu_wqsi_resource_stats_parser.set_defaults(func=peek_hu_wqsi_resource_stats)
    peek_hu_wqse_resource_stats_parser.set_defaults(func=peek_hu_wqse_resource_stats)
    peek_hux_resource_stats_parser.set_defaults(func=peek_hux_resource_stats)
    peek_dam_resource_stats_parser.set_defaults(func=peek_dam_resource_stats)
    peek_bam_resource_stats_parser.set_defaults(func=peek_bam_resource_stats)
    peek_ocm_resource_stats_parser.set_defaults(func=peek_ocm_resource_stats)
    peek_etp_hnu_stats_parser.set_defaults(func=peek_etp_hnu_stats)
    peek_etp_nu_stats_parser.set_defaults(func=peek_etp_nu_stats)
    peek_eqm_stats_parser.set_defaults(func=peek_eqm_stats)
    peek_funtop_stats_parser.set_defaults(func=peek_funtop_stats)
    peek_malloc_agent_stats_parser.set_defaults(func=peek_malloc_agent_stats)
    peek_malloc_agent_non_coh_stats_parser.set_defaults(func=peek_malloc_agent_non_coh_stats)
    peek_wustacks_stats_parser.set_defaults(func=peek_wustacks_stats)
    peek_hu_stats_parser.set_defaults(func=peek_hu_stats)
    peek_hu_stats_pwp_parser.set_defaults(func=peek_hu_pwp_stats)
    peek_hu_stats_pcie_parser.set_defaults(func=peek_hu_pcie_stats)
    peek_hu_stats_fc_parser.set_defaults(func=peek_hu_fc_stats)
    peek_hu_stats_link_parser.set_defaults(func=peek_hu_link_stats)
    peek_hu_framer_stats_parser.set_defaults(func=peek_hu_framer_stats)
    peek_wus_stats_parser.set_defaults(func=peek_wus_stats)
    peek_stats_cdu_parser.set_defaults(func=peek_cdu_stats)
    peek_stats_ca_parser.set_defaults(func=peek_ca_stats)
    peek_stats_ddr_parser.set_defaults(func=peek_ddr_stats)
    peek_stats_mud_parser.set_defaults(func=peek_mud_stats)
    peek_stats_dam_parser.set_defaults(func=peek_dam_stats)
    peek_stats_malloc_caches_parser.set_defaults(func=peek_malloc_caches_stats)
    peek_stats_mbuf_parser.set_defaults(func=peek_mbuf_stats)
    peek_stats_l2_cache_parser.set_defaults(func=peek_l2_cache_stats)
    peek_stats_rdma_parser.set_defaults(func=peek_stats_rdma)
    peek_stats_le_table_sdn_in_parser.set_defaults(func=peek_le_tables_sdn_in)
    peek_stats_le_table_sdn_out_parser.set_defaults(func=peek_le_tables_sdn_out)
    peek_stats_sdn_parser.set_defaults(func=peek_sdn_stats)
    peek_stats_vr_flow_parser.set_defaults(func=peek_vr_flow_stats)
    peek_stats_sdn_meter_parser.set_defaults(func=peek_sdn_meter_stats)
    peek_stats_sdn_flow_parser.set_defaults(func=peek_sdn_flow_stats)
    peek_stats_sdn_vp_parser.set_defaults(func=peek_sdn_vp_stats)
    peek_stats_tcp_parser.set_defaults(func=peek_tcp_stats)
    peek_stats_tcp_flows_summary_parser.set_defaults(func=peek_tcp_flows_summary_stats)
    peek_stats_tcp_flows_details_parser.set_defaults(func=peek_tcp_flows_details)
    #peek_stats_tcp_flow_state_parser.set_defaults(func=peek_tcp_flows_state)
    peek_stats_tcp_flows_state_all_parser.set_defaults(func=peek_tcp_flows_state_all)
    peek_stats_tcp_flows_state_filter_sub_parser.set_defaults(func=peek_tcp_flows_state_filter)
    #peek_stats_tcp_flows_fc_parser.set_defaults(func=peek_tcp_flows_fc)
    peek_stats_tcp_flows_fc_all_parser.set_defaults(func=peek_tcp_flows_fc_all)
    peek_stats_tcp_flows_fc_filter_sub_parser.set_defaults(func=peek_tcp_flows_fc_filter)
    #peek_stats_tcp_flows_stats_parser.set_defaults(func=peek_tcp_flows_stats)
    peek_stats_rate_all_parser.set_defaults(func=peek_stats_rate_all)
    peek_stats_rate_filter_parser.set_defaults(func=peek_stats_rate_filter)
    peek_stats_drops_all_parser.set_defaults(func=peek_stats_drops_all)
    peek_stats_drops_filter_parser.set_defaults(func=peek_stats_drops_filter)
    peek_stats_other_all_parser.set_defaults(func=peek_stats_other_all)
    peek_stats_other_filter_parser.set_defaults(func=peek_stats_other_filter)
    peek_probetest_summary_parser.set_defaults(func=peek_probetest_summary)
    peek_probetest_localityinfo_parser.set_defaults(func=peek_probetest_localityinfo)
    peek_probetest_pathinfo_parser.set_defaults(func=peek_probetest_pathinfo)
    peek_probetest_tunnelinfo_parser.set_defaults(func=peek_probetest_tunnelinfo)
    peek_probetest_streaminfo_parser.set_defaults(func=peek_probetest_streaminfo)
    peek_fcp_nu_gph_parser.set_defaults(func=peek_fcp_nu_gph)
    peek_stats_copp_parser.set_defaults(func=peek_copp_stats)
    peek_stats_rdsock_parser.set_defaults(func=peek_rdsock_stats)
    peek_stats_ssds_parser.set_defaults(func=peek_stats_ssds)
    peek_stats_blt_vol_parser.set_defaults(func=peek_blt_vol_stats)
    peek_stats_rds_vol_parser.set_defaults(func=peek_rds_vol_stats)
    
    # Storage Peek Commands
    peek_storage_vol_parser.set_defaults(func=peek_storage_vols)

    # funos peek fun_malloc Peek commands
    # fun_malloc Peek commands
    peek_fun_malloc_slot_parser.set_defaults(func=peek_fun_malloc_slot_stats)
    # malloc caches slot Peek commands
    peek_malloc_caches_parser.set_defaults(func=peek_malloc_caches_slot_stats)

    # Status peek commands
    peek_status_nhp_parser.set_defaults(func=peek_nhp_status)
    peek_stats_nhp_status_parser.set_defaults(func=peek_stats_nhp_status)
    # -------------- Clear Command Handlers ----------------
    clear_nu_port_stats_parser.set_defaults(func=clear_nu_port_stats)
    clear_nu_fwd_stats_parser.set_defaults(func=clear_nu_fwd_stats)
    clear_nu_erp_stats_parser.set_defaults(func=clear_nu_erp_stats)
    clear_nu_parser_stats_parser.set_defaults(func=clear_nu_parser_stats)
    clear_nu_all_stats_parser.set_defaults(func=clear_nu_all_stats)
    clear_nu_nwqm_stats_parser.set_defaults(func=clear_nu_nwqm_stats)
    clear_nu_vppkts_stats_parser.set_defaults(func=clear_nu_vppkts_stats)

    # -------------- Show Tech Handlers ----------------
    show_tech_nu_parser.set_defaults(func=show_tech_nu_stats)
    show_tech_hnu_parser.set_defaults(func=show_tech_hnu_stats)
    show_tech_all_parser.set_defaults(func=show_tech_all_stats)
    show_tech_k2_parser.set_defaults(func=show_k2_stats)

    # -------------- Flow Command Handlers ----------------
    flow_list_parser.set_defaults(func=get_flow_list)
    flow_list_rdma_parser.set_defaults(func=flow_list_rdma)
    flow_blocked_parser.set_defaults(func=get_flow_blocked)

    # -------------- Debug Command Handlers -----------------
    vp_state_parser.set_defaults(func=debug_vp_state)
    vp_util_parser.set_defaults(func=debug_vp_util)

    # -------------- Storage Command Handlers -----------------
    storage_list_parser.set_defaults(func=storage_list_vols)
    storage_controller_parser.set_defaults(func=storage_list_ctrls)
    storage_device_parser.set_defaults(func=storage_list_dev)
    storage_getsb_parser.set_defaults(func=storage_getsb)
    storage_getinfo_parser.set_defaults(func=storage_getinfo)
    storage_getmap_parser.set_defaults(func=storage_getmap)
    storage_stats_vol_parser.set_defaults(func=storage_vol_stats)
    storage_stats_ctrlr_parser.set_defaults(func=storage_ctrlr_stats)
    storage_stats_device_parser.set_defaults(func=storage_dev_stats)
    base_execute_parser.set_defaults(func=execute_cmd)

    @with_argparser(base_set_parser)
    def do_set(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('set')

    @with_argparser(base_get_parser)
    def do_get(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('get')

    @with_argparser(base_clear_parser)
    def do_clear(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('clear')

    @with_argparser(base_peek_parser)
    def do_peek(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('peek')

    @with_argparser(base_show_parser)
    def do_show(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('show')

    @with_argparser(base_flow_parser)
    def do_flow(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('flow')

    @with_argparser(base_debug_parser)
    def do_debug(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('debug')

    @with_argparser(base_storage_parser)
    def do_storage(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('storage')

    @with_argparser(base_execute_parser)
    def do_execute(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('execute') 

    def __del__(self):
        self.dpc_client.disconnect()


if __name__ == '__main__':
    cmd_obj = CmdController(target_ip="fc200-353-cc", target_port=4223, verbose=False)
    cmd_obj.cmdloop(intro="hello")
