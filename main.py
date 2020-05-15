#!/usr/bin/env python3
from parse import PlaybookParser
from render import render_playbook
import sys, os, logging
import coloredlogs, logging
import error_handling


def setup_loggers(level):
	logger = logging.getLogger('lib')

	field_styles = {'asctime': {'color': 'yellow'}, 'hostname': {'color': 'magenta'}, 'levelname': {'bold': True, 'color': 'magenta'}, 'name': {'color': 'blue'}, 'programname': {'color': 'cyan'}, 'username': {'color': 'yellow'}}

	coloredlogs.install(
		fmt='%(levelname)s: %(message)s',
		level=level,
		field_styles=field_styles,
		logger=logger
	)

	logger = logging.getLogger('main')

	coloredlogs.install(
		fmt='\n%(asctime)s -> %(message)s\n',
		level=level,
		field_styles=field_styles,
		logger=logger
	)
	return logger
	
def main():
	from datetime import datetime
	error_handling.STRICT = False
	logger = setup_loggers("DEBUG")
	pb_path = sys.argv[1]
	from parse import PlaybookParser
	pb = PlaybookParser(pb_path)
	logger.info("RENDERING")
	final_video = render_playbook(pb)
	logger.info("WRITING")
	final_video.write_videofile(os.path.basename(pb_path)+".mp4", fps=30)
	logger.info("FINISH")
	
		
if __name__=='__main__':
	import profile, pstats
	profile.run('main()', 'stats')
	p = pstats.Stats('stats')
	p.sort_stats(pstats.SortKey.TIME, pstats.SortKey.CUMULATIVE).print_stats(20)
