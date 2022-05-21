import helper as h
from Logger import Logger
from Parameter import Parameters

""" Initializing Script Parameters """
args = Parameters(description="Framework project").parse()

""" Initializing Logging Properties """
log_path = args.var_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
log = Logger(log_path).get_logger()


def main():
    log.info("INFO")
    log.debug("DEBUG")
    log.critical("CRITICAL")
    log.error("ERROR")
    log.warning("WARNING")


if __name__ == '__main__':
    main()
