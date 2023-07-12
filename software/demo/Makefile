BUILD_DIR=/home/rik/Documents/Git/LitexTang9KExperiments/build/sipeed_tang_nano_9k
SOC_DIR=/home/rik/Documents/Git/litex/litex/litex/soc/

include $(BUILD_DIR)/software/include/generated/variables.mak
include $(SOC_DIR)/software/common.mak

OBJ_DIR=build

OBJECTS   = $(OBJ_DIR)/crt0.o
OBJECTS   += $(patsubst %.c,%.o,$(wildcard *.c */*.c */*/*.c))

all: demo.bin
	
%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
ifneq ($(OS),Windows_NT)
	chmod -x $@
endif

vpath %.a $(PACKAGES:%=../%)

demo.elf: $(OBJECTS)
	$(CC) $(LDFLAGS) -T linker_mainram.ld -N -o $@ \
		$(OBJECTS) \
		$(PACKAGES:%=-L$(BUILD_DIR)/software/%) \
		-Wl,--whole-archive \
		-Wl,--gc-sections \
		-Wl,-Map,$@.map \
		$(LIBS:lib%=-l%)

ifneq ($(OS),Windows_NT)
	chmod -x $@
endif

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

VPATH = $(BIOS_DIRECTORY):$(BIOS_DIRECTORY)/cmds:$(CPU_DIRECTORY)


$(OBJ_DIR)/%.o: %.cpp
	$(compilexx)

$(OBJ_DIR)/%.o: %.c
	$(compile)

$(OBJ_DIR)/%.o: %.S
	$(assemble)
	@echo $(OBJECTS)

clean:
	$(RM) $(OBJECTS) $(OBJECTS:.o=.d) demo.elf demo.bin .*~ *~ *.d

.PHONY: all clean
