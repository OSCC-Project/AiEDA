import argparse

class Arguements:
    @classmethod
    def parse(cls, sys_args):
        parser = argparse.ArgumentParser(
            description='AiEDA argument management', formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("--team_name", type=str, default="iEDA")
        parser.add_argument("--project_name", type=str, default="gcd")
        parser.add_argument("--experiment_name", type=str, default=None)
        parser.add_argument("--scenario_name", type=str, default="test_sweep")
        parser.add_argument("--wandb_log_path", type=str, default="./wandb_results/")
        parser.add_argument("--wandb_mode",type=str, choices=["offline", "online"],default="offline", help="[WANDB] wandb optimization mode")
        parser.add_argument("--seed",type=int,default=0)
        parser.add_argument("--sweep_worker_num",type=int,default=1)
        parser.add_argument("--num_threads",type=int,default=1)
        parser.add_argument("--config_path",type=str,default="/home/zhanghongda/test_aieda/workspace_old/config/iEDA_config/pl_default_config.json")
        parser.add_argument("--flows",type=str,default=None)
        parser.add_argument("--step",type=str,default="full_flow", help='''
                                NoStep = ""
                                initFlow = "initFlow"
                                initDB = "initDB"
                                edi = "edi"
                                floorplan = "floorplan"
                                pdn = "PDN"
                                prePlace = "prePlace"
                                place = "place"
                                globalPlace = "gp"
                                detailPlace = "dp"
                                cts = "CTS"
                                route = "route"
                                fixFanout = "fixFanout"
                                optDrv = "optDrv"
                                optHold = "optHold"
                                optSetup = "optSetup"
                                legalization = "legalization"
                                full_flow = 'full_flow'
                                custom_flow = 'custom_flow'
                            ''')
        parser.add_argument("--result_dir",type=str,default="./result")
        parser.add_argument("--gpu",type=int,default=0)
        parser.add_argument("--disable_gpu",type=int,default=None)
        parser.add_argument("--gpu_analyze",type=int,default=0)
        parser.add_argument("--sweep_id",type=str,default=None)
        parser.add_argument("--run_count",type=int,default=10)
        parser.add_argument("--plot_flag",type=int,default=0)
        parser.add_argument("--tuner",type=str,default="wandb", choices=["wandb", "nni", "optuna"], help="setting tuner method")
        parser.add_argument("--multobj_flag",type=int,default=0, choices=[1, 0], help="multiple objective optimization")
        parser.add_argument("--store_ref",type=int,default=0, choices=[1, 0], help="store current metric to ref")
        parser.add_argument("--root", type=str, default="/home/zhanghongda/test_aieda/workspace_old", help="workspace root diretory name")
        parser.add_argument("--tech", type=str, default="28nm", help="technology design")
        parser.add_argument("--benchmark_flag", type=bool, default=False, help="weather to generate benchmark")
        parser.add_argument("--benchmark_output", type=str, default="benchmark_output", help="benchmark output path")
        all_args = parser.parse_known_args(sys_args)[0]
        return all_args