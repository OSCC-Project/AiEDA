#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json.py
@Author : yell
@Desc : json parser for feature
'''

from ...utility.json_parser import JsonParser
from ..database import *

class FeatureParserJson(JsonParser):
    """feature parser"""

    def get_summary(self):
        ''' get design data '''
        if self.read() is False:
            return None

        feature_summary = FeatureSummary()

        if 'Design Information' in self.json_data:
            dict_info = self.json_data['Design Information']

            info = SummaryInfo()

            info.eda_tool = dict_info['eda_tool']
            info.eda_version = dict_info['eda_version']
            info.design_name = dict_info['design_name']
            info.design_version = dict_info['design_version']
            info.flow_stage = dict_info['flow_stage']
            info.flow_runtime = dict_info['flow_runtime']
            info.flow_memory = dict_info['flow_memory']

            feature_summary.info = info

        if 'Design Layout' in self.json_data:
            dict_layout = self.json_data['Design Layout']

            layout = SummaryLayout()

            layout.design_dbu = dict_layout['design_dbu']
            layout.core_bounding_height = dict_layout['core_bounding_height']
            layout.core_bounding_width = dict_layout['core_bounding_width']
            layout.core_usage = dict_layout['core_usage']
            layout.core_area = dict_layout['core_area']
            layout.die_bounding_height = dict_layout['die_bounding_height']
            layout.die_bounding_width = dict_layout['die_bounding_width']
            layout.die_usage = dict_layout['die_usage']
            layout.die_area = dict_layout['die_area']

            feature_summary.layout = layout

        if 'Design Statis' in self.json_data:
            dict_statis = self.json_data['Design Statis']

            statis = SummaryStatis()
            statis.num_layers = dict_statis['num_layers']
            statis.num_layers_cut = dict_statis['num_layers_cut']
            statis.num_layers_routing = dict_statis['num_layers_routing']
            statis.num_instances = dict_statis['num_instances']
            statis.num_nets = dict_statis['num_nets']
            statis.num_pdn = dict_statis['num_pdn']
            statis.num_iopins = dict_statis['num_iopins']

            feature_summary.statis = statis

        if 'Layers' in self.json_data:
            dict_layers = self.json_data['Layers']

            summary_layers = SummaryLayers()
            summary_layers.num_layers = dict_layers['num_layers']
            summary_layers.num_layers_routing = dict_layers['num_layers_routing']
            summary_layers.num_layers_cut = dict_layers['num_layers_cut']

            dict_routing_layers = dict_layers['routing_layers']
            for dict_routing_layer in dict_routing_layers:
                routing_layer = SummaryLayerRouting()

                routing_layer.layer_name = dict_routing_layer['layer_name']
                routing_layer.layer_order = dict_routing_layer['layer_order']
                routing_layer.wire_len = dict_routing_layer['wire_len']
                routing_layer.wire_ratio = dict_routing_layer['wire_ratio']
                routing_layer.wire_num = dict_routing_layer['wire_num']
                routing_layer.patch_num = dict_routing_layer['patch_num']

                summary_layers.routing_layers.append(routing_layer)

            dict_cut_layers = dict_layers['cut_layers']
            for dict_cut_layer in dict_cut_layers:
                cut_layer = SummaryLayerCut()

                cut_layer.layer_name = dict_cut_layer['layer_name']
                cut_layer.layer_order = dict_cut_layer['layer_order']
                cut_layer.via_num = dict_cut_layer['via_num']
                cut_layer.via_ratio = dict_cut_layer['via_ratio']

                summary_layers.cut_layers.append(cut_layer)

            feature_summary.layers = summary_layers

        if 'Instances' in self.json_data:
            dict_instances = self.json_data['Instances']

            summary_insts = SummaryInstances()

            total = SummaryInstance()
            total.num = dict_instances['total']['num']
            total.num_ratio = dict_instances['total']['num_ratio']
            total.area = dict_instances['total']['area']
            total.area_ratio = dict_instances['total']['area_ratio']
            total.die_usage = dict_instances['total']['die_usage']
            total.core_usage = dict_instances['total']['core_usage']
            total.pin_num = dict_instances['total']['pin_num']
            total.pin_ratio = dict_instances['total']['pin_ratio']
            summary_insts.total = total

            iopads = SummaryInstance()
            iopads.num = dict_instances['iopads']['num']
            iopads.num_ratio = dict_instances['iopads']['num_ratio']
            iopads.area = dict_instances['iopads']['area']
            iopads.area_ratio = dict_instances['iopads']['area_ratio']
            iopads.die_usage = dict_instances['iopads']['die_usage']
            iopads.core_usage = dict_instances['iopads']['core_usage']
            iopads.pin_num = dict_instances['iopads']['pin_num']
            iopads.pin_ratio = dict_instances['iopads']['pin_ratio']
            summary_insts.iopads = iopads

            macros = SummaryInstance()
            macros.num = dict_instances['macros']['num']
            macros.num_ratio = dict_instances['macros']['num_ratio']
            macros.area = dict_instances['macros']['area']
            macros.area_ratio = dict_instances['macros']['area_ratio']
            macros.die_usage = dict_instances['macros']['die_usage']
            macros.core_usage = dict_instances['macros']['core_usage']
            macros.pin_num = dict_instances['macros']['pin_num']
            macros.pin_ratio = dict_instances['macros']['pin_ratio']
            summary_insts.macros = macros

            logic = SummaryInstance()
            logic.num = dict_instances['logic']['num']
            logic.num_ratio = dict_instances['logic']['num_ratio']
            logic.area = dict_instances['logic']['area']
            logic.area_ratio = dict_instances['logic']['area_ratio']
            logic.die_usage = dict_instances['logic']['die_usage']
            logic.core_usage = dict_instances['logic']['core_usage']
            logic.pin_num = dict_instances['logic']['pin_num']
            logic.pin_ratio = dict_instances['logic']['pin_ratio']
            summary_insts.logic = logic

            clock = SummaryInstance()
            clock.num = dict_instances['clock']['num']
            clock.num_ratio = dict_instances['clock']['num_ratio']
            clock.area = dict_instances['clock']['area']
            clock.area_ratio = dict_instances['clock']['area_ratio']
            clock.die_usage = dict_instances['clock']['die_usage']
            clock.core_usage = dict_instances['clock']['core_usage']
            clock.pin_num = dict_instances['clock']['pin_num']
            clock.pin_ratio = dict_instances['clock']['pin_ratio']
            summary_insts.clock = clock

            feature_summary.instances = summary_insts

        if 'Nets' in self.json_data:
            dict_nets = self.json_data['Nets']

            nets = SummaryNets()

            nets.num_total = dict_nets['num_total']
            nets.num_signal = dict_nets['num_signal']
            nets.num_clock = dict_nets['num_clock']
            nets.num_pins = dict_nets['num_pins']
            nets.num_segment = dict_nets['num_segment']
            nets.num_via = dict_nets['num_via']
            nets.num_wire = dict_nets['num_wire']
            nets.num_patch = dict_nets['num_patch']
            nets.wire_len = dict_nets['wire_len']
            nets.wire_len_signal = dict_nets['wire_len_signal']
            nets.ratio_signal = dict_nets['ratio_signal']
            nets.wire_len_clock = dict_nets['wire_len_clock']
            nets.ratio_clock = dict_nets['ratio_clock']

            feature_summary.nets = nets

        if 'Pins' in self.json_data:
            dict_pins = self.json_data['Pins']

            summary_pins = SummaryPins()

            summary_pins.max_fanout = dict_pins['max_fanout']

            for dict_pin in dict_pins['pin_distribution']:
                pin = SummaryPin()

                if dict_pin['pin_num'] == '> 32':
                    pin.pin_num = 33
                else:
                    pin.pin_num = dict_pin['pin_num']
                pin.net_num = dict_pin['net_num']
                pin.net_ratio = dict_pin['net_ratio']
                # pin.inst_num = dict_pin['inst_num']
                # pin.inst_ratio = dict_pin['inst_ratio']

                summary_pins.pin_distribution.append(pin)

            feature_summary.pins = summary_pins

        return feature_summary

    def get_tools(self):
        ''' get design data '''
        if self.read() is False:
            return None

        feature_tools = FeatureTools()
        feature_tools.no_summary = self.get_tools_netopt()
        feature_tools.place_summary = self.get_tools_place(step='place')
        feature_tools.cts_summary = self.get_tools_cts()
        feature_tools.opt_drv_summary = self.get_tools_timing_opt(
            step='optDrv')
        feature_tools.opt_hold_summary = self.get_tools_timing_opt(
            step='optHold')
        feature_tools.opt_setup_summary = self.get_tools_timing_opt(
            step='optSetup')
        feature_tools.legalization_summary = self.get_tools_legalization(
            step='legalization')
        feature_tools.routing_summary = self.get_tools_route()

        return feature_tools

    def get_eval(self):
        ''' get design data '''
        if self.read() is False:
            return None

        feature_eval = FeatureEval()
        feature_eval.wirelength = self.get_eval_wirelength()
        feature_eval.density = self.get_eval_density()
        feature_eval.congestion = self.get_eval_congestion()
        feature_eval.timing = self.get_eval_timing()

        return feature_eval

    def get_tools_netopt(self):
        if 'fixFanout' in self.json_data:
            dict_netopt = self.json_data['fixFanout']

            no_summary = NetOptSummary()

            for dict_clock_timing in dict_netopt['clocks_timing']:
                clock_timing_cmp = NOClockTimingCmp()
                clock_timing_cmp.clock_name = dict_clock_timing['clock_name']

                origin = ClockTiming()
                origin.setup_tns = dict_clock_timing['origin_setup_tns']
                origin.setup_wns = dict_clock_timing['origin_setup_wns']
                origin.hold_tns = dict_clock_timing['origin_hold_tns']
                origin.hold_wns = dict_clock_timing['origin_hold_wns']
                origin.suggest_freq = dict_clock_timing['origin_suggest_freq']
                clock_timing_cmp.origin = origin

                opt = ClockTiming()
                opt.setup_tns = dict_clock_timing['opt_setup_tns']
                opt.setup_wns = dict_clock_timing['opt_setup_wns']
                opt.hold_tns = dict_clock_timing['opt_hold_tns']
                opt.hold_wns = dict_clock_timing['opt_hold_wns']
                opt.suggest_freq = dict_clock_timing['opt_suggest_freq']
                clock_timing_cmp.opt = opt

                delta = ClockTiming()
                delta.setup_tns = dict_clock_timing['delta_setup_tns']
                delta.setup_wns = dict_clock_timing['delta_setup_wns']
                delta.hold_tns = dict_clock_timing['delta_hold_tns']
                delta.hold_wns = dict_clock_timing['delta_hold_wns']
                delta.suggest_freq = dict_clock_timing['delta_suggest_freq']
                clock_timing_cmp.delta = delta

                no_summary.clock_timings.append(clock_timing_cmp)

            return no_summary

        return None

    def get_tools_cts(self):
        if 'CTS' in self.json_data:
            dict_cts = self.json_data['CTS']

            cts_summary = CTSSummary()

            cts_summary.buffer_num = dict_cts['buffer_num']
            cts_summary.buffer_area = dict_cts['buffer_area']
            cts_summary.clock_path_min_buffer = dict_cts['clock_path_min_buffer']
            cts_summary.clock_path_max_buffer = dict_cts['clock_path_max_buffer']
            cts_summary.max_level_of_clock_tree = dict_cts['max_level_of_clock_tree']
            cts_summary.max_clock_wirelength = dict_cts['max_clock_wirelength']
            cts_summary.total_clock_wirelength = dict_cts['total_clock_wirelength']

            for dict_clock_timing in dict_cts['clocks_timing']:
                clock_timing = ClockTiming()

                clock_timing.clock_name = dict_clock_timing['clock_name']
                clock_timing.setup_tns = dict_clock_timing['setup_tns']
                clock_timing.setup_wns = dict_clock_timing['setup_wns']
                clock_timing.hold_tns = dict_clock_timing['hold_tns']
                clock_timing.hold_wns = dict_clock_timing['hold_wns']
                clock_timing.suggest_freq = dict_clock_timing['suggest_freq']

                cts_summary.clocks_timing.append(clock_timing)

            return cts_summary

        return None

    def get_tools_place(self, step):
        if step not in self.json_data or self.json_data[step] == None:
            return None

        key = step

        dict_pl = self.json_data[key]

        pl_summary = PlaceSummary()

        pl_summary.bin_number = dict_pl['bin_number']
        pl_summary.bin_size_x = dict_pl['bin_size_x']
        pl_summary.bin_size_y = dict_pl['bin_size_y']
        pl_summary.fix_inst_cnt = dict_pl['fix_inst_cnt']
        pl_summary.instance_cnt = dict_pl['instance_cnt']
        pl_summary.net_cnt = dict_pl['net_cnt']
        pl_summary.overflow_number = dict_pl['overflow_number']
        pl_summary.overflow = dict_pl['overflow']
        pl_summary.total_pins = dict_pl['total_pins']

        if 'dplace' in dict_pl:
            dict_dplace = dict_pl['dplace']
            dplace = PLCommonSummary()
            dplace.place_density = dict_dplace['place_density']
            dplace.HPWL = dict_dplace['HPWL']
            dplace.STWL = dict_dplace['STWL']
            pl_summary.dplace = dplace

        if 'gplace' in dict_pl:
            dict_gplace = dict_pl['gplace']
            gplace = PLCommonSummary()
            gplace.place_density = dict_gplace['place_density']
            gplace.HPWL = dict_gplace['HPWL']
            gplace.STWL = dict_gplace['STWL']

            pl_summary.gplace = gplace

        if 'legalization' in dict_pl:
            dict_legalization = dict_pl['legalization']
            lg_summary = LGSummary()
            lg_summary.lg_total_movement = dict_legalization['lg_total_movement']
            lg_summary.lg_max_movement = dict_legalization['lg_max_movement']

            pl_common_summary = PLCommonSummary()
            pl_common_summary.place_density = dict_legalization['place_density']
            pl_common_summary.HPWL = dict_legalization['HPWL']
            pl_common_summary.STWL = dict_legalization['STWL']
            lg_summary.pl_common_summary = pl_common_summary

            pl_summary.lg_summary = lg_summary

        return pl_summary
    
    def get_tools_legalization(self, step):
        if step not in self.json_data or self.json_data[step] == None:
            return None

        key = step

        dict_pl = self.json_data[key]

        lg_summary = LGSummary()
        lg_summary.lg_total_movement = dict_pl['total_movement']
        lg_summary.lg_max_movement = dict_pl['max_movement']

        pl_common_summary = PLCommonSummary()
        pl_common_summary.HPWL = dict_pl['HPWL']
        pl_common_summary.STWL = dict_pl['STWL']
        lg_summary.pl_common_summary = pl_common_summary


        return lg_summary

    def get_tools_route(self):
        if 'route' not in self.json_data:
            return None
        
        dict_route = self.json_data['route']
        rt_summary = RouteSummary()

        if 'PA' in dict_route:
            dict_pa_list = dict_route['PA']
            if isinstance(dict_pa_list, list):
                for dict_pa in dict_pa_list:
                    iter_num = dict_pa.get('iter', 0)
                    pa_summary = PASummary()
                    
                    if 'routing_wire_length_map' in dict_pa:
                        for key, value in dict_pa['routing_wire_length_map'].items():
                            pa_summary.routing_wire_length_map[int(key)] = float(value)
                    
                    pa_summary.total_wire_length = dict_pa.get('total_wire_length', 0.0)
                    
                    if 'cut_via_num_map' in dict_pa:
                        for key, value in dict_pa['cut_via_num_map'].items():
                            pa_summary.cut_via_num_map[int(key)] = int(value)
                    
                    pa_summary.total_via_num = dict_pa.get('total_via_num', 0)
                    
                    if 'routing_patch_num_map' in dict_pa:
                        for key, value in dict_pa['routing_patch_num_map'].items():
                            pa_summary.routing_patch_num_map[int(key)] = int(value)
                    
                    pa_summary.total_patch_num = dict_pa.get('total_patch_num', 0)
                    
                    if 'routing_violation_num_map' in dict_pa:
                        for key, value in dict_pa['routing_violation_num_map'].items():
                            pa_summary.routing_violation_num_map[int(key)] = int(value)
                    
                    pa_summary.total_violation_num = dict_pa.get('total_violation_num', 0)
                    
                    rt_summary.iter_pa_summary_map[iter_num] = pa_summary

        if 'SA' in dict_route:
            dict_sa = dict_route['SA']
            sa_summary = SASummary()
            
            if 'routing_supply_map' in dict_sa:
                for key, value in dict_sa['routing_supply_map'].items():
                    sa_summary.routing_supply_map[int(key)] = int(value)
            
            sa_summary.total_supply = dict_sa.get('total_supply', 0)
            rt_summary.sa_summary = sa_summary

        if 'TG' in dict_route:
            dict_tg = dict_route['TG']
            tg_summary = TGSummary()
            
            tg_summary.total_demand = dict_tg.get('total_demand', 0.0)
            tg_summary.total_overflow = dict_tg.get('total_overflow', 0.0)
            tg_summary.total_wire_length = dict_tg.get('total_wire_length', 0.0)
            
            if 'clock_timing_map' in dict_tg:
                for clock_name, timing_data in dict_tg['clock_timing_map'].items():
                    if isinstance(timing_data, dict):
                        for timing_type, value in timing_data.items():
                            if clock_name not in tg_summary.clock_timing_map:
                                tg_summary.clock_timing_map[clock_name] = {}
                            tg_summary.clock_timing_map[clock_name][timing_type] = float(value)
            
            if 'type_power_map' in dict_tg:
                for power_type, value in dict_tg['type_power_map'].items():
                    tg_summary.type_power_map[power_type] = float(value)
            
            rt_summary.tg_summary = tg_summary

        if 'LA' in dict_route:
            dict_la = dict_route['LA']
            la_summary = LASummary()
            
            if 'routing_demand_map' in dict_la:
                for key, value in dict_la['routing_demand_map'].items():
                    la_summary.routing_demand_map[int(key)] = float(value)
            
            la_summary.total_demand = dict_la.get('total_demand', 0.0)
            
            if 'routing_overflow_map' in dict_la:
                for key, value in dict_la['routing_overflow_map'].items():
                    la_summary.routing_overflow_map[int(key)] = float(value)
            
            la_summary.total_overflow = dict_la.get('total_overflow', 0.0)
            
            if 'routing_wire_length_map' in dict_la:
                for key, value in dict_la['routing_wire_length_map'].items():
                    la_summary.routing_wire_length_map[int(key)] = float(value)
            
            la_summary.total_wire_length = dict_la.get('total_wire_length', 0.0)
            
            if 'cut_via_num_map' in dict_la:
                for key, value in dict_la['cut_via_num_map'].items():
                    la_summary.cut_via_num_map[int(key)] = int(value)
            
            la_summary.total_via_num = dict_la.get('total_via_num', 0)
            
            if 'clock_timing_map' in dict_la:
                for clock_name, timing_data in dict_la['clock_timing_map'].items():
                    if isinstance(timing_data, dict):
                        for timing_type, value in timing_data.items():
                            if clock_name not in la_summary.clock_timing_map:
                                la_summary.clock_timing_map[clock_name] = {}
                            la_summary.clock_timing_map[clock_name][timing_type] = float(value)
            
            if 'type_power_map' in dict_la:
                for power_type, value in dict_la['type_power_map'].items():
                    la_summary.type_power_map[power_type] = float(value)
            
            rt_summary.la_summary = la_summary
        
        if 'SR' in dict_route:
            dict_sr_list = dict_route['SR']
            if isinstance(dict_sr_list, list):
                for dict_sr in dict_sr_list:
                    iter_num = dict_sr.get('iter', 0)
                    sr_summary = SRSummary()
                    
                    if 'routing_demand_map' in dict_sr:
                        for key, value in dict_sr['routing_demand_map'].items():
                            sr_summary.routing_demand_map[int(key)] = float(value)
                    
                    sr_summary.total_demand = dict_sr.get('total_demand', 0.0)
                    
                    if 'routing_overflow_map' in dict_sr:
                        for key, value in dict_sr['routing_overflow_map'].items():
                            sr_summary.routing_overflow_map[int(key)] = float(value)
                    
                    sr_summary.total_overflow = dict_sr.get('total_overflow', 0.0)
                    
                    if 'routing_wire_length_map' in dict_sr:
                        for key, value in dict_sr['routing_wire_length_map'].items():
                            sr_summary.routing_wire_length_map[int(key)] = float(value)
                    
                    sr_summary.total_wire_length = dict_sr.get('total_wire_length', 0.0)
                    
                    if 'cut_via_num_map' in dict_sr:
                        for key, value in dict_sr['cut_via_num_map'].items():
                            sr_summary.cut_via_num_map[int(key)] = int(value)
                    
                    sr_summary.total_via_num = dict_sr.get('total_via_num', 0)
                    
                    if 'clock_timing_map' in dict_sr:
                        for clock_name, timing_data in dict_sr['clock_timing_map'].items():
                            if isinstance(timing_data, dict):
                                for timing_type, value in timing_data.items():
                                    if clock_name not in sr_summary.clock_timing_map:
                                        sr_summary.clock_timing_map[clock_name] = {}
                                    sr_summary.clock_timing_map[clock_name][timing_type] = float(value)
                    
                    if 'type_power_map' in dict_sr:
                        for power_type, value in dict_sr['type_power_map'].items():
                            sr_summary.type_power_map[power_type] = float(value)
                    
                    rt_summary.iter_sr_summary_map[iter_num] = sr_summary
        
        if 'TA' in dict_route:
            dict_ta = dict_route['TA']
            ta_summary = TASummary()
            
            if 'routing_wire_length_map' in dict_ta:
                for key, value in dict_ta['routing_wire_length_map'].items():
                    ta_summary.routing_wire_length_map[int(key)] = float(value)
            
            ta_summary.total_wire_length = dict_ta.get('total_wire_length', 0.0)
            
            if 'routing_violation_num_map' in dict_ta:
                for key, value in dict_ta['routing_violation_num_map'].items():
                    ta_summary.routing_violation_num_map[int(key)] = int(value)
            
            ta_summary.total_violation_num = dict_ta.get('total_violation_num', 0)
            
            rt_summary.ta_summary = ta_summary
        
        if 'DR' in dict_route:
            dict_dr_list = dict_route['DR']
            if isinstance(dict_dr_list, list):
                for dict_dr in dict_dr_list:
                    iter_num = dict_dr.get('iter', 0)
                    dr_summary = DRSummary()
                    
                    if 'routing_wire_length_map' in dict_dr:
                        for key, value in dict_dr['routing_wire_length_map'].items():
                            dr_summary.routing_wire_length_map[int(key)] = float(value)
                    
                    dr_summary.total_wire_length = dict_dr.get('total_wire_length', 0.0)
                    
                    if 'cut_via_num_map' in dict_dr:
                        for key, value in dict_dr['cut_via_num_map'].items():
                            dr_summary.cut_via_num_map[int(key)] = int(value)
                    
                    dr_summary.total_via_num = dict_dr.get('total_via_num', 0)
                    
                    if 'routing_patch_num_map' in dict_dr:
                        for key, value in dict_dr['routing_patch_num_map'].items():
                            dr_summary.routing_patch_num_map[int(key)] = int(value)
                    
                    dr_summary.total_patch_num = dict_dr.get('total_patch_num', 0)
                    
                    if 'routing_violation_num_map' in dict_dr:
                        for key, value in dict_dr['routing_violation_num_map'].items():
                            dr_summary.routing_violation_num_map[int(key)] = int(value)
                    
                    dr_summary.total_violation_num = dict_dr.get('total_violation_num', 0)
                    
                    if 'clock_timing_map' in dict_dr:
                        for clock_name, timing_data in dict_dr['clock_timing_map'].items():
                            if isinstance(timing_data, dict):
                                for timing_type, value in timing_data.items():
                                    if clock_name not in dr_summary.clock_timing_map:
                                        dr_summary.clock_timing_map[clock_name] = {}
                                    dr_summary.clock_timing_map[clock_name][timing_type] = float(value)
                    
                    if 'type_power_map' in dict_dr:
                        for power_type, value in dict_dr['type_power_map'].items():
                            dr_summary.type_power_map[power_type] = float(value)
                    
                    rt_summary.iter_dr_summary_map[iter_num] = dr_summary
        
        if 'VR' in dict_route:
            dict_vr = dict_route['VR']
            vr_summary = VRSummary()
            
            if 'routing_wire_length_map' in dict_vr:
                for key, value in dict_vr['routing_wire_length_map'].items():
                    vr_summary.routing_wire_length_map[int(key)] = float(value)
            
            vr_summary.total_wire_length = dict_vr.get('total_wire_length', 0.0)
            
            if 'cut_via_num_map' in dict_vr:
                for key, value in dict_vr['cut_via_num_map'].items():
                    vr_summary.cut_via_num_map[int(key)] = int(value)
            
            vr_summary.total_via_num = dict_vr.get('total_via_num', 0)
            
            if 'routing_patch_num_map' in dict_vr:
                for key, value in dict_vr['routing_patch_num_map'].items():
                    vr_summary.routing_patch_num_map[int(key)] = int(value)
            
            vr_summary.total_patch_num = dict_vr.get('total_patch_num', 0)
            
            if 'within_net_routing_violation_type_num_map' in dict_vr:
                for layer_key, violation_types in dict_vr['within_net_routing_violation_type_num_map'].items():
                    layer_num = int(layer_key)
                    if isinstance(violation_types, dict):
                        for violation_type, count in violation_types.items():
                            if layer_num not in vr_summary.within_net_routing_violation_type_num_map:
                                vr_summary.within_net_routing_violation_type_num_map[layer_num] = {}
                            vr_summary.within_net_routing_violation_type_num_map[layer_num][violation_type] = int(count)
            
            if 'within_net_violation_type_num_map' in dict_vr:
                for violation_type, count in dict_vr['within_net_violation_type_num_map'].items():
                    vr_summary.within_net_violation_type_num_map[violation_type] = int(count)
            
            if 'within_net_routing_violation_num_map' in dict_vr:
                for key, value in dict_vr['within_net_routing_violation_num_map'].items():
                    vr_summary.within_net_routing_violation_num_map[int(key)] = int(value)
            
            vr_summary.within_net_total_violation_num = dict_vr.get('within_net_total_violation_num', 0)
            
            if 'among_net_routing_violation_type_num_map' in dict_vr:
                for layer_key, violation_types in dict_vr['among_net_routing_violation_type_num_map'].items():
                    layer_num = int(layer_key)
                    if isinstance(violation_types, dict):
                        for violation_type, count in violation_types.items():
                            if layer_num not in vr_summary.among_net_routing_violation_type_num_map:
                                vr_summary.among_net_routing_violation_type_num_map[layer_num] = {}
                            vr_summary.among_net_routing_violation_type_num_map[layer_num][violation_type] = int(count)
            
            if 'among_net_violation_type_num_map' in dict_vr:
                for violation_type, count in dict_vr['among_net_violation_type_num_map'].items():
                    vr_summary.among_net_violation_type_num_map[violation_type] = int(count)
            
            if 'among_net_routing_violation_num_map' in dict_vr:
                for key, value in dict_vr['among_net_routing_violation_num_map'].items():
                    vr_summary.among_net_routing_violation_num_map[int(key)] = int(value)
            
            vr_summary.among_net_total_violation_num = dict_vr.get('among_net_total_violation_num', 0)
            
            if 'clock_timing_map' in dict_vr:
                for clock_name, timing_data in dict_vr['clock_timing_map'].items():
                    if isinstance(timing_data, dict):
                        for timing_type, value in timing_data.items():
                            if clock_name not in vr_summary.clock_timing_map:
                                vr_summary.clock_timing_map[clock_name] = {}
                            vr_summary.clock_timing_map[clock_name][timing_type] = float(value)
            
            if 'type_power_map' in dict_vr:
                for power_type, value in dict_vr['type_power_map'].items():
                    vr_summary.type_power_map[power_type] = float(value)
            
            rt_summary.vr_summary = vr_summary
        
        if 'ER' in dict_route:
            dict_er = dict_route['ER']
            er_summary = ERSummary()
            
            if 'routing_demand_map' in dict_er:
                for key, value in dict_er['routing_demand_map'].items():
                    er_summary.routing_demand_map[int(key)] = int(value)
            
            er_summary.total_demand = dict_er.get('total_demand', 0)
            
            if 'routing_overflow_map' in dict_er:
                for key, value in dict_er['routing_overflow_map'].items():
                    er_summary.routing_overflow_map[int(key)] = int(value)
            
            er_summary.total_overflow = dict_er.get('total_overflow', 0)
            
            if 'routing_wire_length_map' in dict_er:
                for key, value in dict_er['routing_wire_length_map'].items():
                    er_summary.routing_wire_length_map[int(key)] = float(value)
            
            er_summary.total_wire_length = dict_er.get('total_wire_length', 0.0)
            
            if 'cut_via_num_map' in dict_er:
                for key, value in dict_er['cut_via_num_map'].items():
                    er_summary.cut_via_num_map[int(key)] = int(value)
            
            er_summary.total_via_num = dict_er.get('total_via_num', 0)
            
            if 'clock_timing_map' in dict_er:
                for clock_name, timing_data in dict_er['clock_timing_map'].items():
                    if isinstance(timing_data, dict):
                        for timing_type, value in timing_data.items():
                            if clock_name not in er_summary.clock_timing_map:
                                er_summary.clock_timing_map[clock_name] = {}
                            er_summary.clock_timing_map[clock_name][timing_type] = float(value)
            
            if 'type_power_map' in dict_er:
                for power_type, value in dict_er['type_power_map'].items():
                    er_summary.type_power_map[power_type] = float(value)
            
            rt_summary.er_summary = er_summary
        
        return rt_summary

    def get_tools_timing_opt(self, step: str):
        """optDrv, optHold, optSetup"""
        if step not in self.json_data or self.json_data[step] == None:
            return None

        key = step
        to_summary = TimingOptSummary()

        dict_to = self.json_data[key]

        to_summary.HPWL = dict_to['HPWL']
        to_summary.STWL = dict_to['STWL']

        for dict_clock_timing in dict_to['clocks_timing']:
            clock_timing_cmp = TOClockTimingCmp()

            clock_timing_cmp.clock_name = dict_clock_timing['clock_name']

            origin = TOClockTiming()
            origin.tns = dict_clock_timing['origin_tns']
            origin.wns = dict_clock_timing['origin_wns']
            origin.suggest_freq = dict_clock_timing['origin_suggest_freq']
            clock_timing_cmp.origin = origin

            opt = TOClockTiming()
            opt.tns = dict_clock_timing['opt_tns']
            opt.wns = dict_clock_timing['opt_wns']
            opt.suggest_freq = dict_clock_timing['opt_suggest_freq']
            clock_timing_cmp.opt = opt

            delta = TOClockTiming()
            delta.tns = dict_clock_timing['delta_tns']
            delta.wns = dict_clock_timing['delta_wns']
            delta.suggest_freq = dict_clock_timing['delta_suggest_freq']
            clock_timing_cmp.delta = delta
            to_summary.clock_timings.append(clock_timing_cmp)

        return to_summary