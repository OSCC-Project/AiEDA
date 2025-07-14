#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : jsonl.py
@Author : yell
@Desc : jsonl parser for feature
'''
from ...utility.jsonl_parser import JsonlParser
from ..database import *

from typing import Dict, Any

class FeatureParserJsonl(JsonlParser):
    def __init__(self, jsonl_path: str):
        super().__init__(jsonl_path)
        self.read()

    def get_eval(self) -> FeatureEval:
        """Get all evaluation features"""
        eval_features = FeatureEval(
            wirelength=FeatureWirelength(),
            density=FeatureDensity(),
            congestion=FeatureCongestion(),
            timing=FeatureTimingIEDA()
        )

        for data in self.jsonl_data:
            if 'Wirelength' in data:
                eval_features.wirelength = self.get_eval_wirelength(data)
            elif 'Density' in data:
                eval_features.density = self.get_eval_density(data)
            elif 'Congestion' in data:
                eval_features.congestion = self.get_eval_congestion(data)
            elif 'Timing' in data:
                eval_features.timing = self.get_eval_timing(data)
            elif 'Power' in data:
                self.add_power_to_timing(eval_features.timing, data)

        return eval_features

    def get_eval_wirelength(self, data: Dict[str, Any]) -> FeatureWirelength:
        dict_wirelength = data['Wirelength']
        return FeatureWirelength(
            FLUTE=dict_wirelength.get('FLUTE'),
            GRWL=dict_wirelength.get('GRWL'),
            HPWL=dict_wirelength.get('HPWL'),
            HTree=dict_wirelength.get('HTree'),
            VTree=dict_wirelength.get('VTree')
        )

    def get_eval_density(self, data: Dict[str, Any]) -> FeatureDensity:
        dict_density = data['Density']
        return FeatureDensity(
            cell=FeatureDensityCell(
                allcell_density=dict_density['cell'].get('allcell_density'),
                macro_density=dict_density['cell'].get('macro_density'),
                stdcell_density=dict_density['cell'].get('stdcell_density')
            ),
            margin=FeatureDensityMargin(
                horizontal=dict_density['margin'].get('horizontal'),
                union=dict_density['margin'].get('union'),
                vertical=dict_density['margin'].get('vertical')
            ),
            net=FeatureDensityNet(
                allnet_density=dict_density['net'].get('allnet_density'),
                global_net_density=dict_density['net'].get(
                    'global_net_density'),
                local_net_density=dict_density['net'].get('local_net_density')
            ),
            pin=FeatureDensityPin(
                allcell_pin_density=dict_density['pin'].get(
                    'allcell_pin_density'),
                macro_pin_density=dict_density['pin'].get('macro_pin_density'),
                stdcell_pin_density=dict_density['pin'].get(
                    'stdcell_pin_density')
            )
        )

    def get_eval_congestion(self, data: Dict[str, Any]) -> FeatureCongestion:
        dict_congestion = data['Congestion']
        return FeatureCongestion(
            map=FeatureCongestionMap(
                egr=self._get_congestion_map_base(
                    dict_congestion['map'].get('egr', {})),
                lutrudy=self._get_congestion_map_base(
                    dict_congestion['map'].get('lutrudy', {})),
                rudy=self._get_congestion_map_base(
                    dict_congestion['map'].get('rudy', {}))
            ),
            overflow=FeatureCongestionOverflow(
                max=self._get_congestion_overflow_base(
                    dict_congestion['overflow'].get('max', {})),
                top_average=self._get_congestion_overflow_base(
                    dict_congestion['overflow'].get('top average', {})),
                total=self._get_congestion_overflow_base(
                    dict_congestion['overflow'].get('total', {}))
            ),
            utilization=FeatureCongestionUtilization(
                lutrudy=self._get_congestion_utilization_base(
                    dict_congestion['utilization'].get('lutrudy', {}).get('max', {})),
                rudy=self._get_congestion_utilization_base(
                    dict_congestion['utilization'].get('rudy', {}).get('max', {}))
            )
        )

    def _get_congestion_map_base(self, dict_map_base: Dict[str, Any]) -> FeatureCongestionMapBase:
        return FeatureCongestionMapBase(
            horizontal=dict_map_base.get('horizontal'),
            union=dict_map_base.get('union'),
            vertical=dict_map_base.get('vertical')
        )

    def _get_congestion_overflow_base(self, dict_overflow_base: Dict[str, Any]) -> FeatureCongestionOverflowBase:
        return FeatureCongestionOverflowBase(
            horizontal=dict_overflow_base.get('horizontal'),
            union=dict_overflow_base.get('union'),
            vertical=dict_overflow_base.get('vertical')
        )

    def _get_congestion_utilization_base(self, dict_utilization_base: Dict[str, Any]) -> FeatureCongestionUtilizationBase:
        return FeatureCongestionUtilizationBase(
            horizontal=dict_utilization_base.get('horizontal'),
            union=dict_utilization_base.get('union'),
            vertical=dict_utilization_base.get('vertical')
        )

    def get_eval_timing(self, data: Dict[str, Any]) -> FeatureTimingIEDA:
        dict_timing = data['Timing']
        timing = FeatureTimingIEDA()
        for method in ['EGR', 'FLUTE', 'HPWL', 'SALT']:
            if method in dict_timing:
                clock_timings = []
                for clock_data in dict_timing[method]:
                    clock_timing = ClockTiming(
                        clock_name=clock_data.get('clock_name'),
                        hold_tns=clock_data.get('hold_tns'),
                        hold_wns=clock_data.get('hold_wns'),
                        setup_tns=clock_data.get('setup_tns'),
                        setup_wns=clock_data.get('setup_wns'),
                        suggest_freq=clock_data.get('suggest_freq')
                    )
                    clock_timings.append(clock_timing)
                method_timing = MethodTimingIEDA(clock_timings=clock_timings)
                setattr(timing, method, method_timing)
            else:
                print(f"No data for {method} in timing data")
        return timing

    def add_power_to_timing(self, timing: FeatureTimingIEDA, data: Dict[str, Any]) -> FeatureTimingIEDA:
        dict_power = data['Power']
        for method in ['EGR', 'FLUTE', 'HPWL', 'SALT']:
            if method in dict_power:
                method_timing = getattr(timing, method, None)
                if method_timing is None:
                    print(f"Creating new MethodTiming for {method}")
                    method_timing = MethodTimingIEDA(clock_timings=[])
                    setattr(timing, method, method_timing)
                method_timing.static_power = dict_power[method].get(
                    'static_power')
                method_timing.dynamic_power = dict_power[method].get(
                    'dynamic_power')
            else:
                print(f"No power data for {method}")
        return timing
