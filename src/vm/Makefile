# Builds the PyMite VM as an archive
#
# This Makefile is not meant to be invoked directly.
# This Makefile is meant to be invoked by a Makefile in src/platform/<plat>/
# and requires the following environment variables to be exported by the caller:
#   CC OBJCOPY NM CFLAGS AR IPM PM_LIB_FN PLATFORM
#
# The primary function of this makefile is to:
#
#   1. Build pmstdlib_img.c and pmstdlib_nat.c from PMSTDLIB_SOURCES
#   2. Build libpmvm_<plat>.a from all *.c files
#


# PLATFORM = avr_da

ARFLAGS = rcs
SOURCES = $(wildcard *.c) 
OBJECTS = $(SOURCES:.c=.o)
INDENT := $(call pathsearch,indent)


# If RM does not exist, define it as REMOVE
ifeq ($(RM),)
    RM = $(REMOVE)
endif


.PHONY: all size indent clean
# Must delete/rebuild these intermediate files because they depend on the platform
#.INTERMEDIATE: $(SOURCE_IMG) $(SOURCE_NAT)

# Default action is to build the object files
all : $(OBJECTS)



# Build the standard library into an image file and native function file
pm_generated_objs.c pm_generated_types.h : $(PMSTDLIB_SOURCES) $(PMIMGCREATOR)
	$(PMIMGCREATOR) ../vm  $(PMSTDLIB_SOURCES)

size : $(PM_LIB_FN)
	@$(SIZE) $(PM_LIB_FN)

# Runs GNU indent on the source files
indent :
	$(if $(INDENT), $(INDENT) *.c *.h)

# Remove files made by default make
clean :
	@$(RM) $(PM_LIB_FN) 
#	@$(RM) $(OBJECTS)
