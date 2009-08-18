# Makefile for data

WWW=mb312@cirl.berkeley.edu:www/nipy-data

.PHONY: help clean clean_templates clean_data all 
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  templates      make nipy-templates package"
	@echo "  data           make nipy-data package"
	@echo "  clean          clean existing builds of the packages"


clean: clean_templates clean_data

clean_templates:
	-rm -rf nipy-templates/dist

clean_data:
	-rm -rf nipy-data/dist

all: templates data

templates: clean_templates
	python scripts/validata_data_pkg.py nipy-templates

data: clean_data
	python scripts/validata_data_pkg.py nipy-data

publish_templates: 
	rsync -avH nipy-templates/dist/*.zip $(WWW)

publish_data:
	rsync -avH nipy-data/dist/*.zip $(WWW)