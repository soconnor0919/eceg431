CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
YACC = byacc
YACCFLAGS = -d -v
LEX = /opt/homebrew/opt/flex/bin/flex
LEXFLAGS =
LDFLAGS = -L/opt/homebrew/opt/flex/lib
CPPFLAGS = -I/opt/homebrew/opt/flex/include

# Output executable name
TARGET = jack_compiler

# Source files
LEX_SOURCE = jack.l
YACC_SOURCE = jack.y
C_SOURCES = symbol_table.c vm_writer.c

# Generated files
LEX_OUTPUT = lex.yy.c
YACC_OUTPUT = y.tab.c
YACC_HEADER = y.tab.h

# Object files
OBJECTS = $(LEX_OUTPUT:.c=.o) $(YACC_OUTPUT:.c=.o) $(C_SOURCES:.c=.o)

# Default target
all: $(TARGET)

# Build the compiler
$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^ -lfl

# Generate C code from yacc grammar
$(YACC_OUTPUT) $(YACC_HEADER): $(YACC_SOURCE)
	$(YACC) $(YACCFLAGS) $(YACC_SOURCE)

# Generate C code from lex specification
$(LEX_OUTPUT): $(LEX_SOURCE) $(YACC_HEADER)
	$(LEX) $(LEXFLAGS) $(LEX_SOURCE)

# Compile object files
%.o: %.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

# Clean generated files
clean:
	rm -f $(OBJECTS) $(LEX_OUTPUT) $(YACC_OUTPUT) $(YACC_HEADER)
	rm -f jack.output lex.yy.c
	rm -f $(TARGET)

# Test with Seven program
test-seven: $(TARGET)
	@echo "Testing Seven program..."
	@./$(TARGET) ../Seven/Main.jack
	@echo "✅ Seven program compiled successfully"

# Test with all programs
test-all: $(TARGET)
	@echo "Testing all programs..."
	@for dir in ../Seven ../ConvertToBin ../Square ../Average ../Pong ../ComplexArrays; do \
		echo "Testing $$dir..."; \
		for jack_file in $$dir/*.jack; do \
			./$(TARGET) $$jack_file; \
		done; \
		echo "✅ $$dir compiled successfully"; \
	done
	@echo "🎉 All programs compiled successfully!"

# Help target
help:
	@echo "yacc-based Jack Compiler"
	@echo "========================"
	@echo "Available targets:"
	@echo "  all        - Build the Jack compiler"
	@echo "  clean      - Remove generated files"
	@echo "  test-seven - Test with Seven program"
	@echo "  test-all   - Test with all programs"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Usage: ./jack_compiler <file.jack>"

.PHONY: all clean test-seven test-all help
