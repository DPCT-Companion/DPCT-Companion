import argparse

from tester.parse import run_tester
from warning_fixer.SourceProject import SourceProject

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DPCT-Companion", prog="python main.py")
    subparsers = parser.add_subparsers(dest="command")

    fixer_parser = subparsers.add_parser("fixer", help="Warning fixer")
    fixer_parser.add_argument("-d", "--dpcpp-root-path", type=str, help="Path of dpct out-root", required=True)
    fixer_parser.add_argument("-c", "--cuda-root-path", type=str, help="Path of dpct in-root")
    fixer_parser.add_argument("-o", "--output-path", type=str, help="Output path for the fixed code", required=True)
    fixer_parser.add_argument("-l", "--log-path", type=str, help="Path of dpct log")

    tester_parser = subparsers.add_parser("tester", help="Test harness")
    tester_parser.add_argument("--check", action="store_true", help="Mode of the tests harness.")
    tester_parser.add_argument("-p", "--platform", type=str, default="both", choices=["cuda", "dpcpp", "both"],
                               help="The platform where the tests run.")
    tester_parser.add_argument("config", type=str, help="Path of the configuration file")
    tester_parser.add_argument("reports", type=str, nargs="*", help="Path of the partial report files in mode check.")

    args = parser.parse_args()

    if args.command == "fixer":
        project = SourceProject(dpcpp_root_path=args.dpcpp_root_path,
                                cuda_root_path=args.cuda_root_path,
                                output_path=args.output_path,
                                log_path=args.log_path)
        project.fix_project_warnings()

    elif args.command == "tester":
        if args.check and len(args.reports) != 2:
            parser.error("Two partial reports should be given in check mode.")
        config_path = args.config
        platform = args.platform
        if platform == "both":
            platform = "cuda,dpcpp"
        run_tester(config_path, platform, args.check, args.reports)
