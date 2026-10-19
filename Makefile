#---------------------------------------------------------------------------------
.SUFFIXES:
#---------------------------------------------------------------------------------

ifeq ($(strip $(DEVKITARM)),)
$(error "Please set DEVKITARM in your environment. export DEVKITARM=<path to>devkitARM")
endif

include $(DEVKITARM)/gba_rules

#---------------------------------------------------------------------------------
# the LIBGBA path is defined in gba_rules, but we have to define LIBTONC ourselves
#---------------------------------------------------------------------------------
LIBTONC := $(DEVKITPRO)/libtonc

#---------------------------------------------------------------------------------
# TARGET is the name of the output
# BUILD is the directory where object files & intermediate files will be placed
# SOURCES is a list of directories containing source code
# INCLUDES is a list of directories containing extra header files
# DATA is a list of directories containing binary data
# GRAPHICS is a list of directories containing files to be processed by grit
#
# All directories are specified relative to the project directory where
# the makefile is found
#
#---------------------------------------------------------------------------------
TARGET		:= $(notdir $(CURDIR))
BUILD		:= build
SOURCES		:= $(shell find $(wildcard source) -type d)
INCLUDES	:= $(shell find $(wildcard include) -type d)
DATA		:=
MUSIC		:= music
GRAPHICS	:= graphics

CSV_DIR		:= data
CSV_FILES	:= $(wildcard $(CSV_DIR)/*.csv)
CSV_SFILES	:= $(patsubst $(CSV_DIR)/%.csv,$(BUILD)/%.s,$(CSV_FILES))
CSV_HFILES	:= $(patsubst $(CSV_DIR)/%.csv,$(BUILD)/%.h,$(CSV_FILES))
CSV_READER	:= csv_reader.exe

CHARTS		:= charts
CHART_FILES	:= $(wildcard $(CHARTS)/*.chart)
CHART_SFILES	:= $(patsubst $(CHARTS)/%.chart,$(BUILD)/%.s,$(CHART_FILES))
CHART_HFILES	:= $(patsubst $(CHARTS)/%.chart,$(BUILD)/%.h,$(CHART_FILES))
PYTHON ?= python3
AUDIO_DIR ?=
IMPORTED_HEADER ?=
HOSTCXX ?= g++
# Keep native/container helper binaries separate: their C++ runtimes can differ.
HOST_TOOL_ID := $(shell $(HOSTCXX) -dumpmachine)-$(shell $(HOSTCXX) -dumpversion)
CHART_READER := $(CURDIR)/bin/chart_reader-$(HOST_TOOL_ID)

#---------------------------------------------------------------------------------
# options for code generation
#---------------------------------------------------------------------------------
ARCH	:=	-mthumb -mthumb-interwork

CFLAGS	:=	-g -Wall -O2\
		-mcpu=arm7tdmi -mtune=arm7tdmi\
		$(ARCH)

CFLAGS	+=	$(INCLUDE)

CXXFLAGS	:=	$(CFLAGS) -std=gnu++17 -fno-rtti -fno-exceptions

ASFLAGS	:=	-g $(ARCH)
LDFLAGS	=	-g $(ARCH) -Wl,-Map,$(notdir $*.map)

#---------------------------------------------------------------------------------
# any extra libraries we wish to link with the project
#---------------------------------------------------------------------------------
LIBS	:= -lmm -ltonc


#---------------------------------------------------------------------------------
# list of directories containing libraries, this must be the top level containing
# include and lib.
# the LIBGBA path should remain in this list if you want to use maxmod
#---------------------------------------------------------------------------------
LIBDIRS	:=	$(LIBGBA) $(LIBTONC)

#---------------------------------------------------------------------------------
# no real need to edit anything past this point unless you need to add additional
# rules for different file extensions
#---------------------------------------------------------------------------------


ifneq ($(BUILD),$(notdir $(CURDIR)))
.DEFAULT_GOAL := build
#---------------------------------------------------------------------------------

export OUTPUT	:=	$(CURDIR)/$(TARGET)

export VPATH	:=	$(foreach dir,$(SOURCES),$(CURDIR)/$(dir)) \
			$(foreach dir,$(DATA),$(CURDIR)/$(dir)) \
			$(foreach dir,$(GRAPHICS),$(CURDIR)/$(dir)) \
			$(CURDIR)/$(BUILD)

export DEPSDIR	:=	$(CURDIR)/$(BUILD)

CFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.c)))
CPPFILES	:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.cpp)))
SFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.s))) $(notdir $(CSV_SFILES)) $(notdir $(CHART_SFILES))
PNGFILES	:=	$(foreach dir,$(GRAPHICS),$(notdir $(wildcard $(dir)/*.png)))
BINFILES	:=	$(foreach dir,$(DATA),$(notdir $(wildcard $(dir)/*.*)))

ifneq ($(strip $(MUSIC)),)
	export AUDIOFILES	:=	$(foreach dir,$(notdir $(wildcard $(MUSIC)/*.*)),$(CURDIR)/$(MUSIC)/$(dir))
	BINFILES += soundbank.bin
endif

BINFILES += imported_audio.bin imported_backing.bin

#---------------------------------------------------------------------------------
# use CXX for linking C++ projects, CC for standard C
#---------------------------------------------------------------------------------
ifeq ($(strip $(CPPFILES)),)
#---------------------------------------------------------------------------------
	export LD	:=	$(CC)
#---------------------------------------------------------------------------------
else
#---------------------------------------------------------------------------------
	export LD	:=	$(CXX)
#---------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------

export OFILES_BIN := $(addsuffix .o,$(BINFILES))

export OFILES_SOURCES := $(CPPFILES:.cpp=.o) $(CFILES:.c=.o) $(SFILES:.s=.o)

export OFILES_GRAPHICS := $(PNGFILES:.png=.o)

export OFILES := $(OFILES_BIN) $(OFILES_SOURCES) $(OFILES_GRAPHICS)

export HFILES := imported_chart.hpp imported_audio.hpp $(addsuffix .h,$(subst .,_,$(BINFILES))) $(PNGFILES:.png=.h)

export INCLUDE	:=	$(foreach dir,$(INCLUDES),-iquote $(CURDIR)/$(dir)) \
					$(foreach dir,$(LIBDIRS),-I$(dir)/include) \
					-I$(CURDIR)/$(BUILD)

export LIBPATHS	:=	$(foreach dir,$(LIBDIRS),-L$(dir)/lib)

.PHONY: $(BUILD) clean

#---------------------------------------------------------------------------------
$(CHART_READER): bin/chart_reader.cpp
	$(HOSTCXX) -std=c++17 -O2 -Wall -Wextra $< -o $@

# The default is original synthetic data. Private adapted headers are opt-in.
.PHONY: runtime_input
$(BUILD)/imported_chart.hpp: runtime_input tools/prepare_runtime.py tools/adapt_chart.py tools/chart_importer.py tests/fixtures/runtime/easy.chart $(IMPORTED_HEADER)
	$(PYTHON) tools/prepare_runtime.py --output $@ $(if $(IMPORTED_HEADER),--header "$(IMPORTED_HEADER)")

$(BUILD)/imported_audio.bin $(BUILD)/imported_backing.bin $(BUILD)/imported_audio.hpp &: runtime_input $(BUILD)/imported_chart.hpp tools/build_audio.py tools/audio_prepare.py tools/reactive_prepare.py
	$(PYTHON) tools/build_audio.py --output-dir $(BUILD) $(if $(AUDIO_DIR),--audio-dir "$(AUDIO_DIR)") $(if $(IMPORTED_HEADER),--private-chart)

$(BUILD): $(BUILD)/imported_backing.bin $(BUILD)/imported_audio.bin $(BUILD)/imported_audio.hpp $(BUILD)/imported_chart.hpp $(BUILD)/note.h $(CSV_SFILES) $(CSV_HFILES) $(CHART_SFILES) $(CHART_HFILES)
	@[ -d $@ ] || mkdir -p $@
	@$(PYTHON) tools/validate_holds.py $(BUILD)/imported_chart.hpp --audio-header $(BUILD)/imported_audio.hpp
	@$(MAKE) --no-print-directory -C $(BUILD) -f $(CURDIR)/Makefile
	@$(PYTHON) tools/check_rom_size.py "$(OUTPUT).gba"
	@$(PYTHON) tools/verify_build.py "$(OUTPUT).gba" "$(OUTPUT).elf" --header $(BUILD)/imported_chart.hpp

#---------------------------------------------------------------------------------
clean:
	@echo clean ...
	@rm -fr $(BUILD) $(TARGET).elf $(TARGET).gba

#---------------------------------------------------------------------------------
# Pad file for certain writable cartridges
pad:
	@echo padding to next 4KB ...
	@size=$$(stat -c%s $(TARGET).gba); \
	pad=$$(( (4095 + $$size) & ~4095 )); \
	truncate -s $$pad $(TARGET).gba

#---------------------------------------------------------------------------------
full:
	make clean
	make build
	make pad

#---------------------------------------------------------------------------------
# CSV processing rules (parent directory)
#---------------------------------------------------------------------------------
$(BUILD)/%.s $(BUILD)/%.h : $(CSV_DIR)/%.csv
	@[ -d $(BUILD) ] || mkdir -p $(BUILD)
	@echo "csv_reader $(notdir $<)"
	@$(CSV_READER) $(CURDIR)/$<

#---------------------------------------------------------------------------------
# CHART processing rules (parent directory)
#---------------------------------------------------------------------------------
$(CHART_SFILES) $(CHART_HFILES) $(BUILD)/note.h &: $(CHART_FILES) $(CHART_READER)
	@[ -d $(BUILD) ] || mkdir -p $(BUILD)
	@for chart in $(CHART_FILES); do $(CHART_READER) "$(CURDIR)/$$chart" "$(CURDIR)/$(BUILD)" || exit $$?; done


#---------------------------------------------------------------------------------
else

#---------------------------------------------------------------------------------
# main targets
#---------------------------------------------------------------------------------

$(OUTPUT).gba	:	$(OUTPUT).elf

$(OUTPUT).elf	:	$(OFILES)

$(OFILES_SOURCES) : $(HFILES) $(CSV_HFILES) $(CHART_HFILES)

#---------------------------------------------------------------------------------
# The bin2o rule should be copied and modified
# for each extension used in the data directories
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# rule to build soundbank from music files
#---------------------------------------------------------------------------------
soundbank.bin soundbank.h &: $(AUDIOFILES)
#---------------------------------------------------------------------------------
	@mmutil $^ -osoundbank.bin -hsoundbank.h

#---------------------------------------------------------------------------------
# This rule links in binary data with the .bin extension
#---------------------------------------------------------------------------------
%.bin.o	%_bin.h :	%.bin
#---------------------------------------------------------------------------------
	@echo $(notdir $<)
	@$(bin2o)

#---------------------------------------------------------------------------------
# This rule creates assembly source files using grit
# grit takes an image file and a .grit describing how the file is to be processed
# add additional rules like this for each image extension
# you use in the graphics folders
#---------------------------------------------------------------------------------
%.s %.h &: %.png %.grit
#---------------------------------------------------------------------------------
	@echo "grit $(notdir $<)"
	@grit $< -fts -o$*

# make likes to delete intermediate files. This prevents it from deleting the
# files generated by grit after building the GBA ROM.
.SECONDARY:

-include $(DEPSDIR)/*.d
#---------------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------------
