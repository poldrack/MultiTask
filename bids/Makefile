all: bidsclean bidsify copy
bidsify:
	python bidsify.py
bidsclean:
	rm -rf /Users/poldrack/data_unsynced/multitask/sc1/BIDS/*
copy:
	bash bids_commands.sh
	cp dataset_description.json /Users/poldrack/data_unsynced/multitask/sc1/BIDS
	python fix_metadata.py
validate:
	~/node_modules/bids-validator/bin/bids-validator /Users/poldrack/data_unsynced/multitask/sc1/BIDS
