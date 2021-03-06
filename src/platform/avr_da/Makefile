# Hey Emacs, this is a -*- makefile -*-

# AVR-GCC Makefile template, derived from the WinAVR template (which
# is public domain), believed to be neutral to any flavor of "make"
# (GNU make, BSD make, SysV make)

# PyMite Configuration
PLATFORM = avr_da
PM_LIB_ROOT = pmvm_$(PLATFORM)
PM_LIB_FN = lib$(PM_LIB_ROOT).a
PM_LIB_PATH = ../../vm/$(PM_LIB_FN)
PM_USR_SOURCES = main.py avr.py
PMIMGCREATOR := ../../tools/pmImgCreator.py
PMGENPMFEATURES := ../../tools/pmGenPmFeatures.py
IPM = true
DEBUG = true

# Platform Configuration
MCU = avr128da48
FORMAT = ihex
TARGET = main
F_CPU = 24000000UL
SRC = $(TARGET).c plat.c  $(TARGET)_nat.c $(TARGET)_img.c  pyToC.c avr.c
ASRC =
OPT = 2

# This project uses the AVR-Dx_DFP include files provided in the device series support pack
# the latest version at this time is: 1.0.18
# this is automatically installed with MPLABX v5.35 or later
DEVPACK = "/Applications/microchip/mplabx/v5.35/packs/Microchip/AVR-Dx_DFP/1.0.18"
# otherwise you can download it from: https://packs.download.microchip.com/ 
# note: manually installed packs are found in the user home folder -> uncomment the line below
# DEVPACK = $(HOME)/.mchp_packs/Microchip/AVR-Dx_DFP/1.0.18

# Debugging format.
# Native formats for AVR-GCC's -g are stabs [default], or dwarf-2.
# AVR (extended) COFF requires stabs, plus an avr-objcopy run.
DEBUG_FMT = stabs

# Compiler flag to set the C Standard level.
# c89   - "ANSI" C
# gnu89 - c89 plus GCC extensions
# c99   - ISO C99 standard (not yet fully implemented)
# gnu99 - c99 plus GCC extensions
CSTANDARD = -std=gnu99

# Place -D or -U options here
CDEFS = -DF_CPU=$(F_CPU)
# PyMite CDEFS
ifeq ($(DEBUG),true)
	CDEFS += -g -g$(DEBUG_FMT) -D__DEBUG__=1
endif

# Place -I options here
CINCS = -I../../vm -I "$(abspath .)" -I $(DEVPACK)/include -B $(DEVPACK)/avr-gcc/dev/avr128da48

CDEBUG = -g$(DEBUG_FMT)
CWARN =  -Wall -Wstrict-prototypes #-Werror
CTUNING = -funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums -mconst-data-in-progmem
#CEXTRA = -Wa,-adhlns=$(<:.c=.lst)
CFLAGS = $(CDEBUG) $(CDEFS) $(CINCS) -O$(OPT) $(CWARN) $(CSTANDARD) $(CTUNING) $(CEXTRA)


#ASFLAGS = -Wa,-adhlns=$(<:.S=.lst),-gstabs


#Additional libraries.

# Minimalistic printf version
PRINTF_LIB_MIN = -Wl,-u,vfprintf -lprintf_min

# Floating point printf version (requires MATH_LIB = -lm below)
PRINTF_LIB_FLOAT = -Wl,-u,vfprintf -lprintf_flt

PRINTF_LIB =

# Minimalistic scanf version
SCANF_LIB_MIN = -Wl,-u,vfscanf -lscanf_min

# Floating point + %[ scanf version (requires MATH_LIB = -lm below)
SCANF_LIB_FLOAT = -Wl,-u,vfscanf -lscanf_flt

SCANF_LIB =

#MATH_LIB = -lm

# External memory options

# 64 KB of external RAM, starting after internal RAM (ATmega128!),
# used for variables (.data/.bss) and heap (malloc()).
#EXTMEMOPTS = -Wl,-Tdata=0x801100,--defsym=__heap_end=0x80ffff

# 64 KB of external RAM, starting after internal RAM (ATmega128!),
# only used for heap (malloc()).
#EXTMEMOPTS = -Wl,--defsym=__heap_start=0x801100,--defsym=__heap_end=0x80ffff

EXTMEMOPTS =

#LDMAP = $(LDFLAGS) -Wl,-Map=$(TARGET).map,--cref
LDFLAGS = $(EXTMEMOPTS) $(LDMAP) $(PRINTF_LIB) $(SCANF_LIB) $(MATH_LIB)
# PyMite
LDFLAGS += -L../../vm -l$(PM_LIB_ROOT) -L.


# Programming support using drag 'n drop. Settings and variables.

SHELL = sh
# CC = avr-gcc  # modified to test XC8 2.30 compiler 
CC = xc8-cc
AR = xc8-ar
OBJCOPY = avr-objcopy
OBJDUMP = avr-objdump
SIZE = avr-size
NM = avr-nm
REMOVE = rm -f
MV = mv -f
COPY = cp


# Define all object files.
OBJ = $(SRC:.c=.o) $(ASRC:.S=.o)

# Define all listing files.
LST = $(ASRC:.S=.lst) $(SRC:.c=.lst)

# Combine all necessary flags and optional flags.
# Add target processor to flags.
ALL_CFLAGS = -mmcu=$(MCU) -I. $(CFLAGS)
ALL_ASFLAGS = -mmcu=$(MCU) -I. -x assembler-with-cpp $(ASFLAGS)

TARGET_DRIVE = /Volumes/CURIOSITY/
# TARGET_DRIVE = D:\CURIOSITY\ # uncomment for WINDOWS users

COPY_FLAGS =   
# COPY_FLAGS =  -Y  # uncomment for WINDOWS users 

# Default target.
all: pmfeatures.h pmvm build

build: elf hex eep

elf: $(TARGET).elf
hex: $(TARGET).hex
eep: $(TARGET).eep
lss: $(TARGET).lss
sym: $(TARGET).sym


# Program the device.  
program: $(TARGET).hex $(TARGET).eep
	$(COPY)  $(COPY_FLAGS) $(TARGET).hex $(TARGET_DRIVE)code.hex



# Convert ELF to COFF for use in debugging / simulating in AVR Studio or VMLAB.
COFFCONVERT=$(OBJCOPY) --debugging \
--change-section-address .data-0x800000 \
--change-section-address .bss-0x800000 \
--change-section-address .noinit-0x800000 \
--change-section-address .eeprom-0x810000 


# PyMite: Build the VM archive if it doesn't exist
pmvm : $(PM_LIB_PATH)

$(PM_LIB_PATH) : ../../vm/*.c  ../../vm/*.h  ../../lib/*.py
	make -C ../../vm

$(TARGET)_nat.c $(TARGET)_img.c: $(PM_USR_SOURCES) pmfeatures.py 
	$(PMIMGCREATOR) -f pmfeatures.py -c -u --memspace=flash -o $(TARGET)_img.c --native-file=$(TARGET)_nat.c $(PM_USR_SOURCES)

pmfeatures.h : pmfeatures.py $(PMGENPMFEATURES)
	$(PMGENPMFEATURES) pmfeatures.py > $@

coff: $(TARGET).elf
	$(COFFCONVERT) -O coff-avr $(TARGET).elf $(TARGET).cof


extcoff: $(TARGET).elf
	$(COFFCONVERT) -O coff-ext-avr $(TARGET).elf $(TARGET).cof


.SUFFIXES: .elf .hex .eep .lss .sym

.elf.hex:
	$(OBJCOPY) -O $(FORMAT) -R .eeprom $< $@

.elf.eep:
	-$(OBJCOPY) -j .eeprom --set-section-flags=.eeprom="alloc,load" \
	--change-section-lma .eeprom=0 -O $(FORMAT) $< $@

# Create extended listing file from ELF output file.
.elf.lss:
	$(OBJDUMP) -h -S $< > $@

# Create a symbol table from ELF output file.
.elf.sym:
	$(NM) -n $< > $@



# Link: create ELF output file from object files.
$(TARGET).elf: $(OBJ)
	$(CC) $(ALL_CFLAGS) $(OBJ) --output $@ $(LDFLAGS)


# Compile: create object files from C source files.
.c.o:
	$(CC) -c $(ALL_CFLAGS) $< -o $@ 


# Compile: create assembler files from C source files.
.c.s:
	$(CC) -S $(ALL_CFLAGS) $< -o $@


# Assemble: create object files from assembler source files.
.S.o:
	$(CC) -c $(ALL_ASFLAGS) $< -o $@


# Target: clean project.
clean:
	$(MAKE) -C ../../vm clean
	$(REMOVE) $(TARGET).hex $(TARGET).eep $(TARGET).cof $(TARGET).elf \
	$(TARGET).map $(TARGET).sym $(TARGET).lss \
	$(OBJ) $(LST) $(SRC:.c=.s) $(SRC:.c=.d)
	$(REMOVE) $(TARGET)_img.*
	$(REMOVE) $(TARGET)_nat.*

depend:
	if grep '^# DO NOT DELETE' $(MAKEFILE) >/dev/null; \
	then \
		sed -e '/^# DO NOT DELETE/,$$d' $(MAKEFILE) > \
			$(MAKEFILE).$$$$ && \
		$(MV) $(MAKEFILE).$$$$ $(MAKEFILE); \
	fi
	echo '# DO NOT DELETE THIS LINE -- make depend depends on it.' \
		>> $(MAKEFILE); \
	$(CC) -M -mmcu=$(MCU) $(CDEFS) $(CINCS) $(SRC) $(ASRC) >> $(MAKEFILE)

.PHONY:	all build elf hex eep lss sym program coff extcoff clean depend pmvm

export CC OBJCOPY NM CFLAGS ALL_CFLAGS AR IPM PM_LIB_FN
