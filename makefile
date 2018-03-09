TARFILES = $(wildcard *.tar.gz *.tgz)

define extract_tmpl
$(shell tar tf $(1) | head -1):
	tar zxvf $(1)
# ^
# HARD-TAB
#
endef
TAR_DIRS := $(foreach file, $(TARFILES), $(shell tar tf $(file) | head -1))

default: $(TAR_DIRS)

$(foreach file, $(TARFILES), $(eval $(call extract_tmpl,$(file))))

.PHONY: default
